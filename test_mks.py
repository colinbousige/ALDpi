import ressources.mksserial as mks

mksctrl = mks.MKS()
mksctrl.open()
mksctrl.get_actual_flow(1)
mksctrl.set_setpoint(1, 30)
mksctrl.on_channel(1)
mksctrl.on_all()
mksctrl.get_actual_flow(1)
mksctrl.off_all()
mksctrl.close()