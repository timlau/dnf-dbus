import dbus

bus = dbus.SystemBus()
DBUS_SENDER = bus.get_unique_name()

def check_permission(action):
    proxy = bus.get_object('org.freedesktop.PolicyKit1', '/org/freedesktop/PolicyKit1/Authority')
    authority = dbus.Interface(proxy, dbus_interface='org.freedesktop.PolicyKit1.Authority')
    subject = ('system-bus-name', {'name' : DBUS_SENDER})
    action_id = action
    details = {}
    flags = 1            # AllowUserInteraction flag
    cancellation_id = '' # No cancellation id

    (granted, _, details) = authority.CheckAuthorization(subject, action_id, details, flags, cancellation_id)

    return granted==dbus.Boolean(True)

if __name__ == "__main__":
    print(f'Sender : {DBUS_SENDER}')
    granted = check_permission('dk.rasmil.DnfDbus.read')
    print(granted)

