class DigitalPin:
    def __init__(self, channel):
        self.channel = channel
        # Faci un singur task de scriere, dar îl configurezi corect de la început
        self.write_task = nidaqmx.Task()
        self.read_task = nidaqmx.Task()
        
        self.write_task.do_channels.add_do_chan(self.channel, line_grouping=LineGrouping.CHAN_PER_LINE)
        self.read_task.di_channels.add_di_chan(self.channel, line_grouping=LineGrouping.CHAN_PER_LINE)
        
        # Le pornești o singură dată AICI, la inițializare, nu la fiecare bit!
        self.write_task.start()
        self.read_task.start()

    def set_output(self):
        # În loc să oprești task-uri, doar scrii valoarea 0 ca să tragi linia în LOW
        self.write(0)

    def set_input(self):
        # Pentru I2C pseudo-open-drain, scrii 1 ca să lași pull-up-ul extern să ridice linia
        self.write(1)
    
    def write(self, value):
        data = (c_ubyte * 1)(value)
        self.write_task.write(1, data=data)

    def read(self):
        data = (c_ubyte * 1)()
        self.read_task.read(data)
        return data[0]
    
    def close(self):
        # Le oprești și le cureți doar când închizi tot scriptul, la final
        self.write_task.stop()
        self.write_task.close()
        self.read_task.stop()
        self.read_task.close()
