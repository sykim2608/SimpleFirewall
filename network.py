  +#!/usr/bin/python  
 2   +  
 3   +from mininet.net import Mininet  
 4   +from mininet.node import Controller, RemoteController  
 5   +from mininet.log import setLogLevel, info  
 6   +from mininet.cli import CLI  
 7   +from mininet.topo import Topo  
 8   +from mininet.util import quietRun  
 9   +from mininet.moduledeps import pathCheck  
 10   +  
 11   +from sys import exit  
 12   +import os.path  
 13   +from subprocess import Popen, STDOUT, PIPE  
 14   +  
 15   +IPBASE = '10.3.0.0/16'  
 16   +ROOTIP = '10.3.0.100/16'  
 17   +IPCONFIG = './IP_CONFIG'  
 18   +IP_SETTING={}  
 19   +  
 20   +class simpleTopo(Topo):  
 21   +    "Simple topology for running firewall"  
 22   +  
 23   +    def __init__(self, *args, **kwargs):  
 24   +        Topo.__init__(self, *args, **kwargs)  
 25   +        host1 = self.addHost('host1')  
 26   +        host2 = self.addHost('host2')  
 27   +        host3 = self.addHost('host3')  
 28   +        firewall = self.addSwitch('sw0')  
 29   +        for h in host1, host2, host3:  
 30   +            self.addLink(h, firewall)  
 31   +  
 32   +class simpleController(Controller):  
 33   +    "Simple controller for running firewall"  
 34   +  
 35   +    def __init__(self, name, inNamespace=False, command='controller', cargs='-v ptcp:%d',  
 36   +                cdir=None, ip="127.0.0.1", port=7878, **params):  
 37   +        Controller.__init__(self, name, ip=ip, port=port, **params)  
 38   +  
 39   +    def start(self):  
 40   +        pathCheck(self.command)  
 41   +        cout = '/tmp/' + self.name + '.log'  
 42   +        if self.cdir is not None:  
 43   +            self.cmd('cd' + self.cdir)  
 44   +        self.cmd(self.command, self.cargs % self.port, '>&', cout, '&')  
 45   +  
 46   +    def stop(self):  
 47   +        self.cmd('kill %' + self.command)  
 48   +        self.terminate()  
 49   +  
 50   +def set_default_route(host):  
 51   +    info('*** setting default gateway of host %s\n' % host.name)  
 52   +    if(host.name == 'host1'):  
 53   +        routerip = IP_SETTING['sw0-eth1']  
 54   +    elif(host.name == 'host2'):  
 55   +        routerip = IP_SETTING['sw0-eth2']  
 56   +    elif(host.name == 'host3'):  
 57   +        routerip = IP_SETTING['sw0-eth3']  
 58   +    print host.name, routerip  
 59   +    host.cmd('route add %s/32 dev %s-eth0' % (routerip, host.name))  
 60   +    host.cmd('route add default gw %s dev %s-eth0' % (routerip, host.name))  
 61   +    ips = IP_SETTING[host.name].split(".")   
 62   +    host.cmd('route del -net %s.0.0.0/8 dev %s-eth0' % (ips[0], host.name))  
 63   +  
 64   +def get_ip_setting():  
 65   +    try:  
 66   +        with open(IPCONFIG, 'r') as f:  
 67   +            for line in f:  
 68   +                if( len(line.split()) == 0):  
 69   +                  break  
 70   +                name, ip = line.split()  
 71   +                print name, ip  
 72   +                IP_SETTING[name] = ip  
 73   +            info( '*** Successfully loaded ip settings for hosts\n %s\n' % IP_SETTING)  
 74   +    except EnvironmentError:  
 75   +        exit("Couldn't load config file for ip addresses, check whether %s exists" % IPCONFIG_FILE)  
 76   +  
 77   +def simplenet():  
 78   +    get_ip_setting()  
 79   +    topo = simpleTopo()  
 80   +    info( '*** Creating network\n' )  
 81   +    net = Mininet( topo=topo, controller=RemoteController, ipBase=IPBASE )  
 82   +    net.start()  
 83   +    host1, host2, host3, firewall = net.get( 'host1', 'host2', 'host3', 'sw0')  
 84   +    h1intf = host1.defaultIntf()  
 85   +    h1intf.setIP('%s/8' % IP_SETTING['host1'])  
 86   +    h2intf = host2.defaultIntf()  
 87   +    h2intf.setIP('%s/8' % IP_SETTING['host2'])  
 88   +    h3intf = host3.defaultIntf()  
 89   +    h3intf.setIP('%s/8' % IP_SETTING['host3'])  
 90   +  
 91   +  
 92   +    for host in host1, host2, host3:  
 93   +        set_default_route(host)  
 94   +    CLI( net )  
 95   +    net.stop()  
 96   +  
 97   +  
 98   +if __name__ == '__main__':  
 99   +    setLogLevel( 'info' )  
 100   +    simplenet()  
 101   +  
 102   +  
 103   +  
 104   +  
 105   +  
 106   +  
