import React, { useCallback, useState } from 'react';

import { Button, Modal, HorizontalGroup, VerticalGroup, Field, Input } from '@grafana/ui';
import cn from 'classnames/bind';
import { get, kebabCase } from 'lodash-es';
import { observer } from 'mobx-react';
import { Controller, FormProvider, useForm } from 'react-hook-form';

import { WithPermissionControlTooltip } from 'containers/WithPermissionControl/WithPermissionControlTooltip';
import { useStore } from 'state/useStore';
import { UserActions } from 'utils/authorization/authorization';
import { openErrorNotification } from 'utils/utils';

import styles from './MattermostIntegrationButton.module.css';

const cx = cn.bind(styles);

interface MattermostIntegrationProps {
  disabled?: boolean;
  size?: 'md' | 'lg';
  onUpdate: () => void;
}
export const MattermostIntegrationButton = observer((props: MattermostIntegrationProps) => {
  const { disabled, size = 'md', onUpdate } = props;

  const [showModal, setShowModal] = useState<boolean>(false);

  const onModalCreateCallback = useCallback(() => {
    setShowModal(true);
  }, []);

  const onModalCancelCallback = useCallback(() => {
    setShowModal(false);
  }, []);

  const onModalUpdateCallback = useCallback(() => {
    setShowModal(false);

    onUpdate();
  }, [onUpdate]);

  return (
    <>
      <WithPermissionControlTooltip userAction={UserActions.IntegrationsWrite}>
        <Button size={size} variant="primary" icon="plus" disabled={disabled} onClick={onModalCreateCallback}>
          Add Mattermost channel
        </Button>
      </WithPermissionControlTooltip>
      {showModal && <MattermostChannelForm onHide={onModalCancelCallback} onUpdate={onModalUpdateCallback} />}
    </>
  );
});

interface MattermostCreationModalProps {
  onHide: () => void;
  onUpdate: () => void;
}

interface FormFields {
  teamName: string;
  channelName: string;
}

const MattermostChannelForm = (props: MattermostCreationModalProps) => {
  const { onHide, onUpdate } = props;
  const store = useStore();

  const formMethods = useForm<FormFields>({
    mode: 'onChange',
  });

  const {
    control,
    watch,
    formState: { errors },
    handleSubmit,
  } = formMethods;

  const teamName = watch('teamName');
  const channelName = watch('channelName');

  return (
    <Modal title="Add Mattermost Channel" isOpen closeOnEscape={false} onDismiss={onUpdate}>
      <FormProvider {...formMethods}>
        <form onSubmit={handleSubmit(onCreateChannelCallback)}>
          <VerticalGroup>
            {renderTeamNameInput()}
            {renderChannelNameInput()}
            <HorizontalGroup justify="flex-end">
              <Button variant="secondary" onClick={() => onHide()}>
                Cancel
              </Button>
              <Button type="submit" disabled={!teamName || !channelName} variant="primary">
                Create
              </Button>
            </HorizontalGroup>
          </VerticalGroup>
        </form>
      </FormProvider>
    </Modal>
  );

  function renderTeamNameInput() {
    return (
      <Controller
        name="teamName"
        control={control}
        rules={{ required: 'Team Name is required' }}
        render={({ field }) => (
          <Field
            label="Mattermost Team Name"
            invalid={Boolean(errors['teamName'])}
            error={errors['teamName']?.message}
            className={cx('field')}
          >
            <Input
              {...field}
              className={cx('channelFormField__input')}
              maxLength={50}
              placeholder="Enter Mattermost Team Name"
              autoFocus
            />
          </Field>
        )}
      />
    );
  }

  function renderChannelNameInput() {
    return (
      <Controller
        name="channelName"
        control={control}
        rules={{ required: 'Channel Name is required' }}
        render={({ field }) => (
          <Field
            label="Mattermost Channel Name"
            invalid={Boolean(errors['channelName'])}
            error={errors['teamName']?.message}
            className={cx('field')}
          >
            <Input
              {...field}
              className={cx('channelFormField__input')}
              maxLength={50}
              placeholder="Enter Mattermost Channel Name"
              autoFocus
            />
          </Field>
        )}
      />
    );
  }

  async function onCreateChannelCallback() {
    try {
      await store.mattermostChannelStore.create({
        team_name: kebabCase(teamName),
        channel_name: kebabCase(channelName),
      });
      onUpdate();
    } catch (error) {
      openErrorNotification(get(error, 'response.data.detail', 'error creating channel'));
    }
  }
};
