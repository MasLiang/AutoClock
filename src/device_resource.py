class device_resource:
    def __init__(self, device):
        self.device = device
        self.pll_num = 0
        self.mmcm_num = 0
        self.bufg_num = 0
        self.bufi_num = 0
        self.bufgce_num = 0
        self.bufgctrl_num = 0
        self.bufgmux_num = 0
        self.bufgce_div_num = 0

        self.select_device()

    def select_device(self):
        if self.device=="U280":
            self.pll_num = 0
            self.mmcm_num = 0
            self.bufg_num = 0
            self.bufi_num = 0
            self.bufgce_num = 0
            self.bufgctrl_num = 0
            self.bufgmux_num = 0
            self.bufgce_div_num = 0
            
    
    
