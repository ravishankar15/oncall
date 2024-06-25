import React, { useCallback, useState, useEffect } from 'react';

import { Button, Modal, Icon, HorizontalGroup, VerticalGroup, Field, Input } from '@grafana/ui';
import cn from 'classnames/bind';
import { observer } from 'mobx-react';
import CopyToClipboard from 'react-copy-to-clipboard';

import { Block } from 'components/GBlock/Block';
import { Text } from 'components/Text/Text';
import { WithPermissionControlTooltip } from 'containers/WithPermissionControl/WithPermissionControlTooltip';
import { useStore } from 'state/useStore';
import { UserActions } from 'utils/authorization/authorization';
import { openNotification } from 'utils/utils';

import styles from './MattermostSetupButton.module.css'
const cx = cn.bind(styles)

interface MattermostSetupProps {
  disabled?: boolean;
  size?: 'md' | 'lg';
  onUpdate: () => void;
}

export const MattermostSetupButton = observer((props: MattermostSetupProps) => {
  const {disabled, size = 'md', onUpdate } = props;
  const [showModal, setShowModal] = useState<boolean>(false);
  const onSetupModalHideCallback = useCallback(() => {
    setShowModal(false);
  }, [])
  const onSetupModalCallback = useCallback(() => {
    setShowModal(true);
  }, [])
  const onModalUpdateCallback = useCallback(() => {
    setShowModal(false)
    onUpdate();
  }, [onUpdate]);

  return (
    <>
      <WithPermissionControlTooltip userAction={UserActions.IntegrationsWrite}>
        <Button size={size} variant="primary" icon="plus" disabled={disabled} onClick={onSetupModalCallback}>
          Setup Mattermost
        </Button>
      </WithPermissionControlTooltip>
      {showModal && <MattermostModal onHide={onSetupModalHideCallback} onUpdate={onModalUpdateCallback} />}
    </>
    )
});

interface MattermostModalProps {
  onHide: () => void;
  onUpdate: () => void;
}

const MattermostModal = (props: MattermostModalProps) => {
  const { onHide, onUpdate } = props;
  const store = useStore();
  const { mattermostStore } = store

  const [manifestLink, setManifestLink] = useState<string>();

  useEffect(() => {
    (async () => {
      const res = await mattermostStore.getMattermostSetupDetails();
      setManifestLink(res.manifest_link);
    })();
  }, []);

  return (
    <Modal title="Setup Mattermost" closeOnEscape isOpen onDismiss={onUpdate}>
      <VerticalGroup spacing="md">
        <Block withBackground bordered className={cx('mattermost-block')}>
          <Text type="secondary">
            Use the following link for the manifest file
            <Field className={cx('field-command')}>
              <Input
                id="mattermostManifestLink"
                value={manifestLink}
                suffix={
                  <CopyToClipboard
                    text={manifestLink}
                    onCopy={() => {
                      openNotification('Link is copied')
                    }}
                  >
                    <Icon name="copy"/>
                  </CopyToClipboard>
                }
              />
            </Field>
          </Text>
        </Block>
        <HorizontalGroup justify="flex-end">
          <Button variant="secondary" onClick={onHide}>
            Cancel
          </Button>
          <Button variant="primary" onClick={onUpdate}>
            Done
          </Button>
        </HorizontalGroup>
      </VerticalGroup>
    </Modal>
  );
};
