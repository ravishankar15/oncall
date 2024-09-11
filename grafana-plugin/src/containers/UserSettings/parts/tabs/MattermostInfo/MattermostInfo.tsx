import React, { useCallback } from 'react';

import { Button, VerticalGroup, Icon, HorizontalGroup } from '@grafana/ui';
import cn from 'classnames/bind';

import { Block } from 'components/GBlock/Block';
import { Text } from 'components/Text/Text';
import { WithPermissionControlDisplay } from 'containers/WithPermissionControl/WithPermissionControlDisplay';
import { useStore } from 'state/useStore';
import { UserActions } from 'utils/authorization/authorization';
import { DOCS_MATTERMOST_SETUP } from 'utils/consts';

import styles from './MattermostInfo.module.css';

const cx = cn.bind(styles);

export const MattermostInfo = () => {
  const { mattermostStore } = useStore();

  const handleClickConnectMattermostAccount = useCallback(() => {
    mattermostStore.mattermostLogin();
  }, [mattermostStore]);

  return (
    <WithPermissionControlDisplay userAction={UserActions.UserSettingsWrite}>
      <VerticalGroup spacing="lg">
        <Block bordered withBackground className={cx('mattermost-infoblock', 'u-width-100')}>
          <VerticalGroup align="center" spacing="lg">
            <Text>
              Personal Mattermost connection will allow you to manage alert group in your connected mattermost channel
            </Text>
            <Text>To setup personal mattermost click the button below and login to your mattermost server</Text>

            <Text type="secondary">
              More details in{' '}
              <a href={DOCS_MATTERMOST_SETUP} target="_blank" rel="noreferrer">
                <Text type="link">our documentation</Text>
              </a>
            </Text>
          </VerticalGroup>
        </Block>
        <Button onClick={handleClickConnectMattermostAccount}>
          <HorizontalGroup spacing="xs" align="center">
            <Icon name="external-link-alt" className={cx('external-link-style')} /> Open Mattermost connection page
          </HorizontalGroup>
        </Button>
      </VerticalGroup>
    </WithPermissionControlDisplay>
  );
};
