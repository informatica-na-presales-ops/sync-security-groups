from __future__ import annotations

import apscheduler.schedulers.blocking
import boto3
import botocore.exceptions
import datetime
import logging
import notch
import os
import requests
import signal
import sys
import time

log = notch.make_log('sync_security_groups')


class Config:
    dry_run: bool
    ip_list_format: str
    ip_list_min_length: int
    ip_list_source: str
    repeat: bool
    repeat_interval_hours: int
    security_group_ids: list
    version: str

    def __init__(self):
        _true_values = ('true', '1', 'yes', 'on')

        self.dry_run = os.getenv('DRY_RUN', 'True').lower() in _true_values
        self.ip_list_format = os.getenv('IP_LIST_FORMAT')
        self.ip_list_min_length = int(os.getenv('IP_LIST_MIN_LENGTH', '10'))
        self.ip_list_source = os.getenv('IP_LIST_SOURCE')
        self.repeat = os.getenv('REPEAT', 'false') in _true_values
        self.repeat_interval_hours = int(os.getenv('REPEAT_INTERVAL_HOURS', '6'))
        self.security_group_ids = os.getenv('SECURITY_GROUP_IDS', '').split()
        self.version = os.getenv('APP_VERSION')


def human_duration(duration: int) -> str:
    if duration > 60:
        minutes = duration // 60
        seconds = duration % 60
        return f'{minutes}m{seconds}s'
    return f'{duration}s'


def sync_security_group(config: Config, group_spec: str, new_list: list):
    region_name, _, group_id = group_spec.partition(':')
    log.info(f'Attempting to update security group {group_id} in {region_name}')
    ec2 = boto3.resource('ec2', region_name=region_name)
    sg = ec2.SecurityGroup(group_id)
    try:
        log.info(f'Security group name: {sg.group_name}')
    except botocore.exceptions.ClientError as e:
        if e.response.get('Error').get('Code') == 'InvalidGroup.NotFound':
            log.warning(e.response.get('Error').get('Message'))
            return
        else:
            raise

    # First, loop through the existing inbound rules and remove them if the IP address is not in new_list
    # At the same time, compile a local list of IP addresses that remain in the existing inbound rules
    existing_list = []
    for rule in sg.ip_permissions:
        log.debug(f'Existing inbound rule: {rule}')
        for ip_range in rule.get('IpRanges'):
            ip = ip_range.get('CidrIp')
            if ip in new_list:
                log.debug(f'{ip} is allowed')
                existing_list.append(ip)
            else:
                log.info(f'{ip} will be removed')
                params = {
                    'CidrIp': ip,
                    'IpProtocol': rule.get('IpProtocol'),
                    'DryRun': config.dry_run
                }
                if not rule.get('IpProtocol') == '-1':
                    params['FromPort'] = rule.get('FromPort')
                    params['ToPort'] = rule.get('ToPort')
                try:
                    sg.revoke_ingress(**params)
                except botocore.exceptions.ClientError as e:
                    if e.response.get('Error').get('Code') == 'DryRunOperation':
                        log.warning(e.response.get('Error').get('Message'))
                    else:
                        raise

    # Second, loop through the new list and add new inbound rules if they don't already exist in the security group
    for ip in new_list:
        if ip in existing_list:
            log.debug(f'{ip} is already allowed')
        else:
            log.info(f'{ip} will be added')
            params = {
                'IpPermissions': [
                    {
                        'IpProtocol': '-1',
                        'IpRanges': [
                            {'CidrIp': ip, 'Description': f'synced {datetime.date.today()} by sync-security-groups'}
                        ]
                    }
                ],
                'DryRun': config.dry_run
            }
            try:
                sg.authorize_ingress(**params)
            except botocore.exceptions.ClientError as e:
                if e.response.get('Error').get('Code') == 'DryRunOperation':
                    log.warning(e.response.get('Error').get('Message'))
                else:
                    raise


def get_current_ip_list(config: Config) -> list:
    resp = requests.get(config.ip_list_source)
    resp.raise_for_status()
    if config.ip_list_format == 'plain':
        ip_list = resp.text.splitlines()
        log.info(f'The current IP list has {len(ip_list)} items')
        log.debug(f'Current IP list: {ip_list}')
        return [f'{ip}/32' for ip in ip_list]
    elif config.ip_list_format == 'aws':
        ip_list = resp.json()
        return [i.get('ip_prefix') for i in ip_list.get('prefixes')
                if 'ip_prefix' in i and i.get('service') == 'ROUTE53_HEALTHCHECKS']
    return []


def main_job(config: Config):
    main_job_start = time.monotonic()
    log.info('Running the main job')

    current_list = get_current_ip_list(config)
    if len(current_list) < config.ip_list_min_length:
        log.warning(f'Cannot continue because IP list length is less than {config.ip_list_min_length}')
    else:
        for g in config.security_group_ids:
            sync_security_group(config, g, current_list)

    if config.repeat:
        repeat_message = f'see you again in {config.repeat_interval_hours} hours'
    else:
        repeat_message = 'quitting'

    main_job_duration = int(time.monotonic() - main_job_start)
    log.info(f'Main job completed in {human_duration(main_job_duration)}, {repeat_message}')


def main():
    config = Config()
    if config.repeat:
        log.info(f'This job will repeat every {config.repeat_interval_hours} hours')
        log.info('Change this value by setting the REPEAT_INTERVAL_HOURS environment variable')
        scheduler = apscheduler.schedulers.blocking.BlockingScheduler()
        scheduler.add_job(main_job, 'interval', args=[config], hours=config.repeat_interval_hours)
        scheduler.add_job(main_job, args=[config])
        scheduler.start()
    else:
        main_job(config)


def handle_sigterm(_signal, _frame):
    sys.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_sigterm)
    main()
