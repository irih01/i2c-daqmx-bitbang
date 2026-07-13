class DigitalPin:
    def __init__(self, channel):
        self.channel = channel
        self.write_task = nidaqmx.Task()
        self.read_task = nidaqmx.Task()
        
        self.write_task.do_channels.add_do_chan(self.channel, line_grouping=LineGrouping.CHAN_PER_LINE)
        self.read_task.di_channels.add_di_chan(self.channel, line_grouping=LineGrouping.CHAN_PER_LINE)
        
        self.write_task.start()
        self.read_task.start()

    def set_output(self):
        self.write(0)

    def set_input(self):
        self.write(1)
    
    def write(self, value):
        data = (c_ubyte * 1)(value)
        self.write_task.write(1, data=data)

    def read(self):
        data = (c_ubyte * 1)()
        self.read_task.read(data)
        return data[0]
    
    def close(self):
        self.write_task.stop()
        self.write_task.close()
        self.read_task.stop()
        self.read_task.close()
