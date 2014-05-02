from enigma import eListboxPythonMultiContent, gFont, eEnv
from boxbranding import getBoxType, getMachineName, getMachineBrand, getBrandOEM
from Components.Console import Console
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Network import iNetwork
from Components.NimManager import nimmanager
from Components.SystemInfo import SystemInfo

from Screens.Screen import Screen
from Screens.NetworkSetup import *
from Screens.About import About
from Screens.PluginBrowser import PluginDownloadBrowser, PluginBrowser
from Screens.LanguageSelection import LanguageSelection
from Screens.Satconfig import NimSelection
from Screens.VideoMode import VideoSetup
from Screens.ScanSetup import ScanSimple, ScanSetup
from Screens.Setup import Setup, getSetupTitle
from Screens.HarddiskSetup import HarddiskSelection, HarddiskFsckSelection, HarddiskConvertExt4Selection
from Screens.SkinSelector import LcdSkinSelector

from Plugins.Plugin import PluginDescriptor
from Plugins.SystemPlugins.PositionerSetup.plugin import PositionerSetup, RotorNimSelection
from Plugins.SystemPlugins.Satfinder.plugin import Satfinder
from Plugins.SystemPlugins.NetworkBrowser.MountManager import AutoMountManager
from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
from Plugins.SystemPlugins.NetworkWizard.NetworkWizard import NetworkWizard
#from Plugins.SystemPlugins.Videomode.plugin import VideoSetup
#from Plugins.SystemPlugins.Videomode.VideoHardware import video_hw
from Plugins.Extensions.Infopanel.RestartNetwork import RestartNetwork
from Screens.HddSetup import HddSetup
from Screens.HddMount import HddFastRemove
from Screens.Swap import Swap
from Screens.OpenNFR_wizard import OpenNFRWizardSetup
from Plugins.Extensions.Infopanel.Manager import *
from Plugins.SystemPlugins.SoftwareManager.ImageBackup import ImageBackup
from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin, SoftwareManagerSetup
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import BackupScreen, RestoreScreen, BackupSelection, getBackupPath, getBackupFilename
from Plugins.Extensions.Infopanel.SoftwarePanel import SoftwarePanel
from Plugins.Extensions.Infopanel.e2log import E2log
from Plugins.Extensions.Infopanel.Net_test import Net_test
from Plugins.Extensions.Infopanel.Softcamedit import vEditor
from Plugins.Extensions.Infopanel.Satloader import Satloader
from Plugins.Extensions.Infopanel.InstallTarGZ import InfopanelManagerScreen
from Plugins.Extensions.Infopanel.Flash_local import doFlashImage

from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_SKIN
from Tools.LoadPixmap import LoadPixmap

from os import path, listdir
from time import sleep
from re import search
import sys
import NavigationInstance

plugin_path_networkbrowser = eEnv.resolve("${libdir}/enigma2/python/Plugins/SystemPlugins/NetworkBrowser")
#############################################################################################################
imagePath = '/hdd/images'
flashPath = '/hdd/images/flash'
flashTmp = '/hdd/images/tmp'
ofgwritePath = '/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/data/ofgwrite'
dir_path = '/media/hdd/images/flash'
#############################################################################################################

if path.exists("/usr/lib/enigma2/python/Plugins/Extensions/AudioSync"):
	from Plugins.Extensions.AudioSync.AC3setup import AC3LipSyncSetup
	plugin_path_audiosync = eEnv.resolve("${libdir}/enigma2/python/Plugins/Extensions/AudioSync")
	AUDIOSYNC = True
else:
	AUDIOSYNC = False

if path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.pyo"):
	from Plugins.SystemPlugins.VideoEnhancement.plugin import VideoEnhancementSetup
	VIDEOENH = True
else:
	VIDEOENH = False

if path.exists("/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoResolution/plugin.pyo"):
	from Plugins.SystemPlugins.AutoResolution.plugin import AutoResSetupMenu
	AUTORES = True
else:
	AUTORES = False

if path.exists("/usr/lib/enigma2/python/Plugins/Extensions/dFlash"):
	from Plugins.Extensions.dFlash.plugin import dFlash
	DFLASH = True
else:
	DFLASH = False

def isFileSystemSupported(filesystem):
	try:
		for fs in open('/proc/filesystems', 'r'):
			if fs.strip().endswith(filesystem):
				return True
		return False
	except Exception, ex:
		print "[Harddisk] Failed to read /proc/filesystems:", ex

def Freespace(dev):
	statdev = os.statvfs(dev)
	space = (statdev.f_bavail * statdev.f_frsize) / 1024
	print "[Flash] Free space on %s = %i kilobytes" %(dev, space)
	return space

class QuickMenu(Screen):
	skin = """
		<screen name="QuickMenu" position="center,center" size="1180,600" backgroundColor="black" flags="wfBorder">
		<widget name="list" position="21,32" size="370,400" backgroundColor="black" itemHeight="50" transparent="2" />
		<widget name="sublist" position="410,32" size="300,400" backgroundColor="black" itemHeight="50" />
		<eLabel position="400,30" size="2,400" backgroundColor="darkgrey" zPosition="3" />
		<widget source="session.VideoPicture" render="Pig" position="720,30" size="450,300" backgroundColor="transparent" zPosition="1" />
		<widget name="description" position="22,445" size="1150,110" zPosition="1" font="Regular;22" halign="center" backgroundColor="black" transparent="1" />
		<widget name="key_red" position="20,571" size="300,26" zPosition="1" font="Regular;22" halign="center" foregroundColor="white" backgroundColor="black" transparent="1" />
		<widget name="key_green" position="325,571" size="300,26" zPosition="1" font="Regular;22" halign="center" foregroundColor="white" backgroundColor="black" transparent="1" />
		<widget name="key_yellow" position="630,571" size="300,26" zPosition="1" font="Regular;22" halign="center" foregroundColor="white" backgroundColor="black" transparent="1" valign="center" />
		<widget name="key_blue" position="935,571" size="234,26" zPosition="1" font="Regular;22" halign="center" foregroundColor="white" backgroundColor="black" transparent="1" />
		<eLabel name="new eLabel" position="21,567" size="300,3" zPosition="3" backgroundColor="red" />
		<eLabel name="new eLabel" position="325,567" size="300,3" zPosition="3" backgroundColor="green" />
		<eLabel name="new eLabel" position="630,567" size="300,3" zPosition="3" backgroundColor="yellow" />
		<eLabel name="new eLabel" position="935,567" size="234,3" zPosition="3" backgroundColor="blue" />
		</screen> """

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Quick Launch Menu"))

		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("System Info"))
		self["key_yellow"] = Label(_("Devices"))
		self["key_blue"] = Label()
		self["description"] = Label()

		self.menu = 0
		self.list = []

		self["list"] = QuickMenuList(self.list)
		self.sublist = []
		self["sublist"] = QuickMenuSubList(self.sublist)
		self.selectedList = []
		self.onChangedEntry = []
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self["sublist"].onSelectionChanged.append(self.selectionSubChanged)

		self["actions"] = ActionMap(["SetupActions","WizardActions","MenuActions","MoviePlayerActions"],
		{
			"ok": self.ok,
			"back": self.keyred,
			"cancel": self.keyred,
			"left": self.goLeft,
			"right": self.goRight,
			"up": self.goUp,
			"down": self.goDown,
		}, -1)


		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
			{
			"red": self.keyred,
			"green": self.keygreen,
			"yellow": self.keyyellow,
			})

		self.MainQmenu()
		self.selectedList = self["list"]
		self.selectionChanged()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self["sublist"].selectionEnabled(0)

	def selectionChanged(self):
		if self.selectedList == self["list"]:
			item = self["list"].getCurrent()
			if item:
				self["description"].setText(_(item[4]))
				self.okList()

	def selectionSubChanged(self):
		if self.selectedList == self["sublist"]:
			item = self["sublist"].getCurrent()
			if item:
				self["description"].setText(_(item[3]))

	def goLeft(self):
		if self.menu <> 0:
			self.menu = 0
			self.selectedList = self["list"]
			self["list"].selectionEnabled(1)
			self["sublist"].selectionEnabled(0)
			self.selectionChanged()

	def goRight(self):
		if self.menu == 0:
			self.menu = 1
			self.selectedList = self["sublist"]
			self["sublist"].moveToIndex(0)
			self["list"].selectionEnabled(0)
			self["sublist"].selectionEnabled(1)
			self.selectionSubChanged()

	def goUp(self):
		self.selectedList.up()
		
	def goDown(self):
		self.selectedList.down()
		
	def keyred(self):
		self.close()

	def keygreen(self):
		self.session.open(About)

	def keyyellow(self):
		self.session.open(QuickMenuDevices)

######## Main Menu ##############################
	def MainQmenu(self):
		self.menu = 0
		self.list = []
		self.oldlist = []
		self.list.append(QuickMenuEntryComponent("Software Manager",_("Update/Backup/Restore your box"),_("Update/Backup your firmware, Backup/Restore settings")))
		self.list.append(QuickMenuEntryComponent("Softcam",_("Start/stop/select cam"),_("Start/stop/select your cam, You need to install first a softcam")))
		self.list.append(QuickMenuEntryComponent("AV Setup",_("Setup Videomode"),_("Setup your Video Mode, Video Output and other Video Settings")))		
		self.list.append(QuickMenuEntryComponent("System",_("System Setup"),_("Setup your System")))
		self.list.append(QuickMenuEntryComponent("E2 Log",_("E2 Loggen for Errors"),_("E2 Loggen for Errors")))
		self.list.append(QuickMenuEntryComponent("Harddisk",_("Harddisk Setup"),_("Setup your Harddisk")))		
		self.list.append(QuickMenuEntryComponent("Mounts",_("Mount Setup"),_("Setup your mounts for network")))
		self.list.append(QuickMenuEntryComponent("Network",_("Setup your local network"),_("Setup your local network. For Wlan you need to boot with a USB-Wlan stick")))
		self.list.append(QuickMenuEntryComponent("Tuner Setup",_("Setup Tuner"),_("Setup your Tuner and search for channels")))
		self.list.append(QuickMenuEntryComponent("Plugins",_("Download plugins"),_("Shows available pluigns. Here you can download and install them")))
		self.list.append(QuickMenuEntryComponent("ScreenShot Manager",_("make Screenshot"),_("make your OSD; VIDEO; ALL Screenshots")))
		self["list"].l.setList(self.list)

######## System Setup Menu ##############################
	def Qsystem(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Customise",_("Setup Enigma2"),_("Customise enigma2 personal settings")))
		self.sublist.append(QuickSubMenuEntryComponent("OSD settings",_("Settings..."),_("Setup your OSD")))
		self.sublist.append(QuickSubMenuEntryComponent("Button Setup",_("Button Setup"),_("Setup your remote buttons")))
		if SystemInfo["FrontpanelDisplay"] and SystemInfo["Display"]:
			self.sublist.append(QuickSubMenuEntryComponent("Display Settings",_("Display Setup"),_("Setup your display")))
		if SystemInfo["LcdDisplay"]:
			self.sublist.append(QuickSubMenuEntryComponent("LCD Skin Setup",_("Skin Setup"),_("Setup your LCD")))
		self.sublist.append(QuickSubMenuEntryComponent("Channel selection",_("Channel selection configuration"),_("Setup your Channel selection configuration")))
		self.sublist.append(QuickSubMenuEntryComponent("Recording settings",_("Recording Setup"),_("Setup your recording config")))
		self.sublist.append(QuickSubMenuEntryComponent("EPG settings",_("EPG Setup"),_("Setup your EPG config")))
		self["sublist"].l.setList(self.sublist)

######## Network Menu ##############################
	def Qnetwork(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Network Wizard",_("Configure your Network"),_("Use the Networkwizard to configure your Network. The wizard will help you to setup your network")))
		if len(self.adapters) > 1: # show only adapter selection if more as 1 adapter is installed
			self.sublist.append(QuickSubMenuEntryComponent("Network Adapter Selection",_("Select Lan/Wlan"),_("Setup your network interface. If no Wlan stick is used, you only can select Lan")))
		if not self.activeInterface == None: # show only if there is already a adapter up
			self.sublist.append(QuickSubMenuEntryComponent("Network Interface",_("Setup interface"),_("Setup network. Here you can setup DHCP, IP, DNS")))
		self.sublist.append(QuickSubMenuEntryComponent("Network Restart",_("Restart network to with current setup"),_("Restart network and remount connections")))
		self.sublist.append(QuickSubMenuEntryComponent("Network Services",_("Setup Network Services"),_("Setup Network Services (Samba, Ftp, NFS, ...)")))
		self.sublist.append(QuickSubMenuEntryComponent("iperf Net_test",_("Downloadgeschwindigkeit_test"),_("zusaetzlich die iperf.7z aus Extensions/Infopanel/data auf Pc kopieren und mit iperf.exe -s aus Dos fenster starten")))		
		self["sublist"].l.setList(self.sublist)

#### Network Services Menu ##############################
	def Qnetworkservices(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Network Configs",_("Setup Network configs"),_("enable/disable HBBTV; 3g-4g Modem; Firmwareupdate; Wifi Driver")))
		self.sublist.append(QuickSubMenuEntryComponent("Samba",_("Setup Samba"),_("Setup Samba")))
		self.sublist.append(QuickSubMenuEntryComponent("NFS",_("Setup NFS"),_("Setup NFS")))
		self.sublist.append(QuickSubMenuEntryComponent("FTP",_("Setup FTP"),_("Setup FTP")))
		self.sublist.append(QuickSubMenuEntryComponent("AFP",_("Setup AFP"),_("Setup AFP")))
		self.sublist.append(QuickSubMenuEntryComponent("OpenVPN",_("Setup OpenVPN"),_("Setup OpenVPN")))
		self.sublist.append(QuickSubMenuEntryComponent("MiniDLNA",_("Setup MiniDLNA"),_("Setup MiniDLNA")))
		self.sublist.append(QuickSubMenuEntryComponent("Inadyn",_("Setup Inadyn"),_("Setup Inadyn")))
		self.sublist.append(QuickSubMenuEntryComponent("SABnzbd",_("Setup SABnzbd"),_("Setup SABnzbd")))
		self.sublist.append(QuickSubMenuEntryComponent("uShare",_("Setup uShare"),_("Setup uShare")))
		self.sublist.append(QuickSubMenuEntryComponent("Telnet",_("Setup Telnet"),_("Setup Telnet")))
		self["sublist"].l.setList(self.sublist)

######## Mount Settings Menu ##############################
	def Qmount(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Mount Manager",_("Manage network mounts"),_("Setup your network mounts")))
		self.sublist.append(QuickSubMenuEntryComponent("Network Browser",_("Search for network shares"),_("Search for network shares")))
		self.sublist.append(QuickSubMenuEntryComponent("HDD Manager",_("Mount your Devices"),_("Setup your Device mounts (USB, HDD, others...)")))
		self.sublist.append(QuickSubMenuEntryComponent("HDD Fast Umount",_("Fast Umount your HDD"),_("HDD Fast Umount)")))		
		self.sublist.append(QuickSubMenuEntryComponent("SWAP Manager",_("Manage your SWAP File"),_("Swap File Configuration)")))		
		self["sublist"].l.setList(self.sublist)

######## Softcam Menu ##############################
	def Qsoftcam(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Softcam Panel",_("Control your Softcams"),_("Use the Softcam Panel to control your Cam. This let you start/stop/select a cam")))
		self.sublist.append(QuickSubMenuEntryComponent("Softcam Config Edit",_("Edit your Emu-Configs"),_("Edit your Emu-Configs")))		
		self["sublist"].l.setList(self.sublist)

#### Softcamedit Menu ##############################
	def Qsoftcamedit(self):
		self.sublist = []
		if path.exists("/usr/keys/oscam.server") or path.exists("/usr/keys/oscam.user") or path.exists("/usr/keys/oscam.conf") or path.exists("/usr/keys/oscam.dvbapi"):
			self.sublist.append(QuickSubMenuEntryComponent("Oscam Config Edit",_("Oscam Config Edit"),_("Oscam Config Edit")))
		if path.exists("/usr/keys/CCcam.cfg"):
                	self.sublist.append(QuickSubMenuEntryComponent("CCcam Config Edit",_("CCcam Config Edit"),_("CCcam Config Edit")))
		if path.exists("/usr/keys/mg_cfg") or path.exists("/usr/keys/cccamd.list") or path.exists("/usr/keys/newcamd.list"):
                	self.sublist.append(QuickSubMenuEntryComponent("Mgcamd Config Edit",_("Mgcamd Config Edit"),_("Mgcamd Config Edit")))
		if path.exists("/usr/keys/camd3.config") or path.exists("/usr/keys/camd3.users") or path.exists("/usr/keys/camd3.servers"):
                	self.sublist.append(QuickSubMenuEntryComponent("Camd3 Config Edit",_("Camd3 Config Edit"),_("Camd3 Config Edit")))
		if path.exists("/usr/keys/gbox.cfg") or path.exists("/usr/keys/cwshare.cfg"): 
                	self.sublist.append(QuickSubMenuEntryComponent("Gbox Config Edit",_("Gbox Config Edit"),_("Gbox Config Edit")))
		if path.exists("/usr/keys/wicardd.conf"):
                	self.sublist.append(QuickSubMenuEntryComponent("Wicard Config Edit",_("Wicard Config Edit"),_("Wicard Config Edit")))
		self["sublist"].l.setList(self.sublist)		

#### Oscam Edit Menu ##############################
	def Qoscamedit(self):
		self.sublist = []
		if path.exists("/usr/keys/oscam.server"):
			self.sublist.append(QuickSubMenuEntryComponent("Oscam.server Edit",_("Oscam.server Edit"),_("open Oscam.server to Edit")))
                if path.exists("/usr/keys/oscam.user"):
			self.sublist.append(QuickSubMenuEntryComponent("Oscam.user Edit",_("Oscam.user Edit"),_("open Oscam.user to Edit")))
                if path.exists("/usr/keys/oscam.conf"):
			self.sublist.append(QuickSubMenuEntryComponent("Oscam.conf Edit",_("Oscam.conf Edit"),_("open Oscam.conf to Edit")))
                if path.exists("/usr/keys/oscam.dvbapi"):
			self.sublist.append(QuickSubMenuEntryComponent("Oscam.dvbapi Edit",_("Oscam.dvbapi Edit"),_("open Oscam.dvbapi to Edit")))
		self["sublist"].l.setList(self.sublist)
#### Ccam Edit Menu ##############################
	def QCCcamedit(self):
		self.sublist = []
		if path.exists("/usr/keys/CCcam.cfg"):
			self.sublist.append(QuickSubMenuEntryComponent("CCcam.cfg Edit",_("CCcam.cfg Edit"),_("open CCcam.cfg to Edit")))
		self["sublist"].l.setList(self.sublist)	
#### Mgcamd Edit Menu ##############################
	def QMgcamdedit(self):
		self.sublist = []
		if path.exists("/usr/keys/mg_cfg"):
			self.sublist.append(QuickSubMenuEntryComponent("mg.cfg Edit",_("mg.cfg Edit"),_("open mg.cfg to Edit")))
		if path.exists("/usr/keys/cccamd.list"):
                	self.sublist.append(QuickSubMenuEntryComponent("Mgcamd cccamd.list Edit",_("Mgcamd cccamd.list Edit"),_("open Mgcamd cccamd.list to Edit")))		
		if path.exists("/usr/keys/newcamd.list"):
                	self.sublist.append(QuickSubMenuEntryComponent("Mgcamd newcamd.list Edit",_("Mgcamd newcamd.list Edit"),_("open Mgcamd newcamd.list to Edit")))		
		self["sublist"].l.setList(self.sublist)	
#### Camd3 Edit Menu ##############################
	def QCamd3edit(self):
		self.sublist = []
		if path.exists("/usr/keys/camd3.config"):
			self.sublist.append(QuickSubMenuEntryComponent("camd3.config Edit",_("camd3.config Edit"),_("open camd3.config to Edit")))
		if path.exists("/usr/keys/camd3.users"):
                	self.sublist.append(QuickSubMenuEntryComponent("camd3.users Edit",_("camd3.users Edit"),_("open camd3.users to Edit")))		
		if path.exists("/usr/keys/camd3.servers"):
                	self.sublist.append(QuickSubMenuEntryComponent("camd3.servers Edit",_("camd3.servers Edit"),_("open camd3.servers to Edit")))		
		self["sublist"].l.setList(self.sublist)	
#### Gbox Edit Menu ##############################
	def QGboxedit(self):
		self.sublist = []
		if path.exists("/usr/keys/gbox.cfg"):
			self.sublist.append(QuickSubMenuEntryComponent("gbox.cfg Edit",_("gbox.cfg Edit"),_("open gbox.cfg to Edit")))
		if path.exists("/usr/keys/cwshare.cfg"):
                	self.sublist.append(QuickSubMenuEntryComponent("cwshare.cfg Edit",_("cwshare.cfg Edit"),_("open cwshare.cfg to Edit")))		
		self["sublist"].l.setList(self.sublist)	
#### Wicardd Edit Menu ##############################
	def QWicarddedit(self):
		self.sublist = []
		if path.exists("/usr/keys/wicardd.conf"):
			self.sublist.append(QuickSubMenuEntryComponent("wicardd.conf Edit",_("wicardd.conf Edit"),_("open wicardd.conf to Edit")))
		self["sublist"].l.setList(self.sublist)	
		
######## A/V Settings Menu ##############################
	def Qavsetup(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("AV Settings",_("Setup Videomode"),_("Setup your Video Mode, Video Output and other Video Settings")))
		if AUDIOSYNC == True:
			self.sublist.append(QuickSubMenuEntryComponent("Audio Sync",_("Setup Audio Sync"),_("Setup Audio Sync settings")))
		self.sublist.append(QuickSubMenuEntryComponent("Auto Language",_("Auto Language Selection"),_("Select your Language for Audio/Subtitles")))
		if os_path.exists("/proc/stb/vmpeg/0/pep_apply") and VIDEOENH == True:
			self.sublist.append(QuickSubMenuEntryComponent("VideoEnhancement",_("VideoEnhancement Setup"),_("VideoEnhancement Setup")))
		if AUTORES == True:
			self.sublist.append(QuickSubMenuEntryComponent("AutoResolution",_("AutoResolution Setup"),_("Automatically change resolution")))

		self["sublist"].l.setList(self.sublist)

######## Tuner Menu ##############################
	def Qtuner(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Tuner Configuration",_("Setup tuner(s)"),_("Setup each tuner for your satellite system")))
		self.sublist.append(QuickSubMenuEntryComponent("Positioner Setup",_("Setup rotor"),_("Setup your positioner for your satellite system")))
		self.sublist.append(QuickSubMenuEntryComponent("Automatic Scan",_("Service Searching"),_("Automatic scan for services")))
		self.sublist.append(QuickSubMenuEntryComponent("Manual Scan",_("Service Searching"),_("Manual scan for services")))
		self.sublist.append(QuickSubMenuEntryComponent("Sat Finder",_("Search Sats"),_("Search Sats, check signal and lock")))
		self.sublist.append(QuickSubMenuEntryComponent("Sat Loader",_("Download satellites.xml"),_("Download satellites.xml")))		
		self["sublist"].l.setList(self.sublist)

######## Software Manager Menu ##############################
	def Qsoftware(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Software Update",_("Online software update"),_("Check/Install online updates (you must have a working internet connection)")))
		self.sublist.append(QuickSubMenuEntryComponent("Complete Backup",_("Backup your current image"),_("Backup your current image to HDD or USB. This will make a 1:1 copy of your box")))
		self.sublist.append(QuickSubMenuEntryComponent("Backup Settings",_("Backup your current settings"),_("Backup your current settings. This includes E2-setup, channels, network and all selected files")))
		self.sublist.append(QuickSubMenuEntryComponent("Restore Settings",_("Restore settings from a backup"),_("Restore your settings back from a backup. After restore the box will restart to activated the new settings")))
		self.sublist.append(QuickSubMenuEntryComponent("Select Backup files",_("Choose the files to backup"),_("Here you can select which files should be added to backupfile. (default: E2-setup, channels, network")))
		self.sublist.append(QuickSubMenuEntryComponent("Software Manager Setup",_("Manage your online update files"),_("Here you can select which files should be updated with a online update")))
		if not getBoxType().startswith('az') and not getBoxType().startswith('dream') and not getBoxType().startswith('ebox'):
		    self.sublist.append(QuickSubMenuEntryComponent("Flash Local",_("Flash Local a new image"),_("Flash on the fly your Receiver software.")))		
		self["sublist"].l.setList(self.sublist)

######## Plugins Menu ##############################
	def Qplugin(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Plugin Browser",_("Open the Plugin Browser"),_("Shows Plugins Browser. Here you can setup installed Plugin")))
		self.sublist.append(QuickSubMenuEntryComponent("Download Plugins",_("Download and install Plugins"),_("Shows available plugins. Here you can download and install them")))
		self.sublist.append(QuickSubMenuEntryComponent("Remove Plugins",_("Delete Plugins"),_("Delete and unstall Plugins. This will remove the Plugin from your box")))
		self.sublist.append(QuickSubMenuEntryComponent("Plugin Filter",_("Setup Plugin filter"),_("Setup Plugin filter. Here you can select which Plugins are showed in the PluginBrowser")))
		self.sublist.append(QuickSubMenuEntryComponent("IPK Installer",_("Install local extension"),_("Scan for local extensions and install them")))
		self.sublist.append(QuickSubMenuEntryComponent("PackageManager",_("Install local extension"),_("Scan for local tar/rar/zip Package and install them")))		
		self["sublist"].l.setList(self.sublist)

######## Harddisk Menu ##############################
	def Qharddisk(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("Harddisk Setup",_("Harddisk Setup"),_("Setup your Harddisk")))
		self.sublist.append(QuickSubMenuEntryComponent("Initialization",_("Format HDD"),_("Format your Harddisk")))
		self.sublist.append(QuickSubMenuEntryComponent("Filesystem Check",_("Check HDD"),_("Filesystem check your Harddisk")))
		if isFileSystemSupported("ext4"):
			self.sublist.append(QuickSubMenuEntryComponent("Convert ext3 to ext4",_("Convert filesystem ext3 to ext4"),_("Convert filesystem ext3 to ext4")))
		self["sublist"].l.setList(self.sublist)

	def ok(self):
		if self.menu > 0:
			self.okSubList()
		else:
			self.goRight()
######## E2-Log Menu ##############################
	def Qe2log(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("E2 Log",_("E2 Loggen for Errors"),_("E2 Loggen for Errors")))
		self["sublist"].l.setList(self.sublist)
######## Tar.gz Menu ##############################
	def Qtar(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("PackageManager",_("Install local extension"),_("Scan for local tar/rar/zip Package and install them")))
		self["sublist"].l.setList(self.sublist)		
######## screenshot Menu ##############################
	def Qscreenshot(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent("OSD",_("Screenshot nur OSD"),_("Screenshot nur OSD")))
		self.sublist.append(QuickSubMenuEntryComponent("VIDEO",_("Screenshot nur Video"),_("Screenshot nur Video")))		
		self.sublist.append(QuickSubMenuEntryComponent("ALL",_("Screenshot Video+OSD"),_("Screenshot Video+OSD")))		
		self["sublist"].l.setList(self.sublist)
#####################################################################
######## Make Selection MAIN MENU LIST ##############################
#####################################################################
			
	def okList(self):
		item = self["list"].getCurrent()

######## Select Network Menu ##############################
		if item[0] == _("Network"):
			self.GetNetworkInterfaces()
			self.Qnetwork()
######## Select System Setup Menu ##############################
		elif item[0] == _("System"):
			self.Qsystem()
######## Select Mount Menu ##############################
		elif item[0] == _("Mounts"):
			self.Qmount()
######## Select Softcam Menu ##############################
		elif item[0] == _("Softcam"):
			self.Qsoftcam()
######## Select AV Setup Menu ##############################
		elif item[0] == _("AV Setup"):
			self.Qavsetup()
######## Select Tuner Setup Menu ##############################
		elif item[0] == _("Tuner Setup"):
			self.Qtuner()
######## Select Software Manager Menu ##############################
		elif item[0] == _("Software Manager"):
			self.Qsoftware()
######## Select PluginDownloadBrowser Menu ##############################
		elif item[0] == _("Plugins"):
			self.Qplugin()
######## Select E2-Log Menu ##############################
		elif item[0] == _("E2 Log"):
			self.Qe2log()
######## Select tar Menu ##############################
		elif item[0] == _("PackageManager"):
			self.Qtar()			
######## Select screenshot Menu ##############################
		elif item[0] == _("ScreenShot Manager"):
			self.Qscreenshot()			
######## Select Tuner Setup Menu ##############################
		elif item[0] == _("Harddisk"):
			self.Qharddisk()

		self["sublist"].selectionEnabled(0)

#####################################################################
######## Make Selection SUB MENU LIST ##############################
#####################################################################
			
	def okSubList(self):
		item = self["sublist"].getCurrent()

######## Select Network Menu ##############################
		if item[0] == _("Network Wizard"):
			self.session.open(NetworkWizard)
		elif item[0] == _("Network Adapter Selection"):
			self.session.open(NetworkAdapterSelection)
		elif item[0] == _("Network Interface"):
			self.session.open(AdapterSetup,self.activeInterface)
		elif item[0] == _("Network Restart"):
			self.session.open(RestartNetwork)
		elif item[0] == _("Network Services"):
			self.Qnetworkservices()
			self["sublist"].moveToIndex(0)
		elif item[0] == _("iperf Net_test"):
			self.session.open(Net_test)			
		elif item[0] == _("Samba"):
			self.session.open(NetworkSamba)
		elif item[0] == _("NFS"):
			self.session.open(NetworkNfs)
		elif item[0] == _("FTP"):
			self.session.open(NetworkFtp)
		elif item[0] == _("AFP"):
			self.session.open(NetworkAfp)
		elif item[0] == _("OpenVPN"):
			self.session.open(NetworkOpenvpn)
		elif item[0] == _("MiniDLNA"):
			self.session.open(NetworkMiniDLNA)
		elif item[0] == _("Inadyn"):
			self.session.open(NetworkInadyn)
		elif item[0] == _("SABnzbd"):
			self.session.open(NetworkSABnzbd)
		elif item[0] == _("uShare"):
			self.session.open(NetworkuShare)
		elif item[0] == _("Telnet"):
			self.session.open(NetworkTelnet)
		elif item[0] == _("Network Configs"):
			self.session.open(OpenNFRWizardSetup)			
######## Select System Setup Menu ##############################
		elif item[0] == _("Customise"):
			self.openSetup("usage")
		elif item[0] == _("Button Setup"):
			self.openSetup("remotesetup")
		elif item[0] == _("Display Settings"):
			self.openSetup("display")
		elif item[0] == _("LCD Skin Setup"):
			self.session.open(LcdSkinSelector)
		elif item[0] == _("OSD settings"):
			self.openSetup("userinterface")
		elif item[0] == _("Channel selection"):
			self.openSetup("channelselection")
		elif item[0] == _("Recording settings"):
			self.openSetup("recording")
		elif item[0] == _("EPG settings"):
			self.openSetup("epgsettings")
######## Select Mounts Menu ##############################
		elif item[0] == _("Mount Manager"):
			self.session.open(AutoMountManager, None, plugin_path_networkbrowser)
		elif item[0] == _("Network Browser"):
			self.session.open(NetworkBrowser, None, plugin_path_networkbrowser)
		elif item[0] == _("HDD Manager"):
			self.session.open(HddSetup)
		elif item[0] == _("HDD Fast Umount"):
			self.session.open(HddFastRemove)			
		elif item[0] == _("SWAP Manager"):
			self.session.open(Swap)	
######## Select Softcam Menu ##############################
		elif item[0] == _("Softcam Panel"):
       			self.session.open(NFRCamManager)
       	        elif item[0] == _("Softcam Config Edit"):
			self.Qsoftcamedit()
			self["sublist"].moveToIndex(0)
######## Select OscamEdit Menu ##############################
		elif item[0] == _("Oscam Config Edit"):
			self.Qoscamedit()
			self["sublist"].moveToIndex(0)
######## Select CCcam Config Edit Menu ##############################
		elif item[0] == _("CCcam Config Edit"):
			self.QCCcamedit()
			self["sublist"].moveToIndex(0)			
######## Select Mgcamd Config Edit Menu ##############################
		elif item[0] == _("Mgcamd Config Edit"):
			self.QMgcamdedit()
			self["sublist"].moveToIndex(0)					
######## Select Camd3 Config Edit Menu ##############################
		elif item[0] == _("Camd3 Config Edit"):
			self.QCamd3edit()
			self["sublist"].moveToIndex(0)					
######## Select Gbox Config Edit Menu ##############################
		elif item[0] == _("Gbox Config Edit"):
			self.QGboxedit()
			self["sublist"].moveToIndex(0)					
######## Select Wicard Config Edit Menu ##############################
		elif item[0] == _("Wicard Config Edit"):
			self.QWicarddedit()
			self["sublist"].moveToIndex(0)
		elif item[0] == _("Oscam.server Edit"):
			self.session.open(vEditor, "/usr/keys/oscam.server")	
		elif item[0] == _("Oscam.user Edit"):
			self.session.open(vEditor, "/usr/keys/oscam.user")	
		elif item[0] == _("Oscam.conf Edit"):
			self.session.open(vEditor, "/usr/keys/oscam.conf")	
		elif item[0] == _("Oscam.dvbapi Edit"):
			self.session.open(vEditor, "/usr/keys/oscam.dvbapi")	
		elif item[0] == _("CCcam.cfg Edit"):
			self.session.open(vEditor, "/usr/keys/CCcam.cfg")	
		elif item[0] == _("mg.cfg Edit"):
			self.session.open(vEditor, "/usr/keys/mg_cfg")	
		elif item[0] == _("Mgcamd cccamd.list Edit"):
			self.session.open(vEditor, "/usr/keys/cccamd.list")	
		elif item[0] == _("Mgcamd newcamd.list Edit"):
			self.session.open(vEditor, "/usr/keys/newcamd.list")	
		elif item[0] == _("camd3.config Edit"):
			self.session.open(vEditor, "/usr/keys/camd3.config")	
		elif item[0] == _("camd3.users Edit"):
			self.session.open(vEditor, "/usr/keys/camd3.users")	
		elif item[0] == _("camd3.servers Edit"):
			self.session.open(vEditor, "/usr/keys/camd3.servers")	
		elif item[0] == _("gbox.cfg Edit"):
			self.session.open(vEditor, "/usr/keys/gbox_cfg")	
		elif item[0] == _("cwshare.cfg Edit"):
			self.session.open(vEditor, "/usr/keys/cwshare.cfg")	
		elif item[0] == _("wicardd.conf Edit"):
			self.session.open(vEditor, "/usr/keys/wicardd.conf")				
######## Select Screenshot Menu ##############################
		elif item[0] == _("OSD"):
                        self.Console = Console()
                        self.Console.ePopen("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/data/screenshot.sh o ExecuteOnce")
       		elif item[0] == _("VIDEO"):
       		        self.Console = Console()
                        self.Console.ePopen("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/data/screenshot.sh v ExecuteOnce")
       		elif item[0] == _("ALL"):
       		        self.Console = Console()
                        self.Console.ePopen("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/data/screenshot.sh ExecuteOnce")
                      			
######## Select AV Setup Menu ##############################
		elif item[0] == _("AV Settings"):
			self.session.open(VideoSetup)
		elif item[0] == _("Auto Language"):
			self.openSetup("autolanguagesetup")
		elif item[0] == _("Audio Sync"):
			self.session.open(AC3LipSyncSetup, plugin_path_audiosync)
		elif item[0] == _("VideoEnhancement"):
			self.session.open(VideoEnhancementSetup)
		elif item[0] == _("AutoResolution"):
			self.session.open(AutoResSetupMenu)
######## Select TUNER Setup Menu ##############################
		elif item[0] == _("Tuner Configuration"):
			self.session.open(NimSelection)
		elif item[0] == _("Positioner Setup"):
			self.PositionerMain()
		elif item[0] == _("Automatic Scan"):
			self.session.open(ScanSimple)
		elif item[0] == _("Manual Scan"):
			self.session.open(ScanSetup)
		elif item[0] == _("Sat Finder"):
			self.SatfinderMain()
		elif item[0] == _("Sat Loader"):
			self.session.open(Satloader)			
######## Select Software Manager Menu ##############################
		elif item[0] == _("Software Update"):
			#self.session.open(UpdatePlugin)
			self.session.open(SoftwarePanel)
		elif item[0] == _("Flash Local"):
			if not os.path.exists("/media/hdd"):
			        self.session.open(MessageBox, _("No /hdd found !!\nPlease make sure you have a HDD mounted.\n\nExit plugin."), type = MessageBox.TYPE_ERROR)
			        return False
		        if Freespace('/media/hdd') < 300000:
			        self.session.open(MessageBox, _("Not enough free space on /hdd !!\nYou need at least 300Mb free space.\n\nExit plugin."), type = MessageBox.TYPE_ERROR)
			        return False
         		if not os.path.exists(ofgwritePath):
			        self.session.open(MessageBox, _('ofgwrite not found !!\nPlease make sure you have ofgwrite installed in /usr/lib/enigma2/python/Plugins/Extensions/Infopanel/data/ofgwrite.\n\nExit plugin.'), type = MessageBox.TYPE_ERROR)
			        return False
             		
			else:
			   
                            if os.path.exists(dir_path):
                                 os.system('rm -rf ' + dir_path)
		            if not os.path.exists(imagePath):
                                 os.mkdir(imagePath)
                            if not os.path.exists(dir_path):
                                 os.mkdir(dir_path)
                                 self.session.open(doFlashImage)
                               			
		elif item[0] == _("Complete Backup"):
			if DFLASH == True:
				self.session.open(dFlash)
			else:
				self.session.open(ImageBackup)
		elif item[0] == _("Backup Settings"):
			self.session.openWithCallback(self.backupDone,BackupScreen, runBackup = True)
		elif item[0] == _("Restore Settings"):
			self.backuppath = getBackupPath()
			self.backupfile = getBackupFilename()
			self.fullbackupfilename = self.backuppath + "/" + self.backupfile
			if os_path.exists(self.fullbackupfilename):
				self.session.openWithCallback(self.startRestore, MessageBox, _("Are you sure you want to restore your %s %s backup?\nSTB will restart after the restore") % (getMachineBrand(), getMachineName()))
			else:
				self.session.open(MessageBox, _("Sorry no backups found!"), MessageBox.TYPE_INFO, timeout = 10)
		elif item[0] == _("Select Backup files"):
			self.session.openWithCallback(self.backupfiles_choosen,BackupSelection)
		elif item[0] == _("Software Manager Setup"):
			self.session.open(SoftwareManagerSetup)
######## Select PluginDownloadBrowser Menu ##############################
		elif item[0] == _("Plugin Browser"):
			self.session.open(PluginBrowser)
		elif item[0] == _("Download Plugins"):
			self.session.open(PluginDownloadBrowser, 0)
		elif item[0] == _("Remove Plugins"):
			self.session.open(PluginDownloadBrowser, 1)
		elif item[0] == _("IPK Installer"):
			try:
				from Plugins.Extensions.MediaScanner.plugin import main
				main(self.session)
			except:
				self.session.open(MessageBox, _("Sorry MediaScanner is not installed!"), MessageBox.TYPE_INFO, timeout = 10)
######## Select Harddisk Menu ############################################
		elif item[0] == _("Harddisk Setup"):
			self.openSetup("harddisk")
		elif item[0] == _("Initialization"):
			self.session.open(HarddiskSelection)
		elif item[0] == _("Filesystem Check"):
			self.session.open(HarddiskFsckSelection)
		elif item[0] == _("Convert ext3 to ext4"):
			self.session.open(HarddiskConvertExt4Selection)
######## Select E2-Log Menu ############################################
		elif item[0] == _("E2 Log"):
			self.session.open(E2log)
######## Select tar Menu ############################################
		elif item[0] == _("PackageManager"):
			self.session.open(InfopanelManagerScreen)			
######## OPEN SETUP MENUS ####################
	def openSetup(self, dialog):
		self.session.openWithCallback(self.menuClosed, Setup, dialog)

	def menuClosed(self, *res):
		pass

######## NETWORK TOOLS #######################
	def GetNetworkInterfaces(self):
		self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getAdapterList()]

		if not self.adapters:
			self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getConfiguredAdapters()]

		if len(self.adapters) == 0:
			self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getInstalledAdapters()]

		self.activeInterface = None
	
		for x in self.adapters:
			if iNetwork.getAdapterAttribute(x[1], 'up') is True:
				self.activeInterface = x[1]
				return

######## TUNER TOOLS #######################
	def PositionerMain(self):
		nimList = nimmanager.getNimListOfType("DVB-S")
		if len(nimList) == 0:
			self.session.open(MessageBox, _("No positioner capable frontend found."), MessageBox.TYPE_ERROR)
		else:
			if len(NavigationInstance.instance.getRecordings()) > 0:
				self.session.open(MessageBox, _("A recording is currently running. Please stop the recording before trying to configure the positioner."), MessageBox.TYPE_ERROR)
			else:
				usableNims = []
				for x in nimList:
					configured_rotor_sats = nimmanager.getRotorSatListForNim(x)
					if len(configured_rotor_sats) != 0:
						usableNims.append(x)
				if len(usableNims) == 1:
					self.session.open(PositionerSetup, usableNims[0])
				elif len(usableNims) > 1:
					self.session.open(RotorNimSelection)
				else:
					self.session.open(MessageBox, _("No tuner is configured for use with a diseqc positioner!"), MessageBox.TYPE_ERROR)

	def SatfinderMain(self):
		nims = nimmanager.getNimListOfType("DVB-S")

		nimList = []
		for x in nims:
			if not nimmanager.getNimConfig(x).configMode.getValue() in ("loopthrough", "satposdepends", "nothing"):
				nimList.append(x)

		if len(nimList) == 0:
			self.session.open(MessageBox, _("No satellite frontend found!!"), MessageBox.TYPE_ERROR)
		else:
			if len(NavigationInstance.instance.getRecordings()) > 0:
				self.session.open(MessageBox, _("A recording is currently running. Please stop the recording before trying to start the satfinder."), MessageBox.TYPE_ERROR)
			else:
				if len(nimList) == 1:
					self.session.open(Satfinder)
				#else:
				#	self.session.open(SatNimSelection)

		
######## SOFTWARE MANAGER TOOLS #######################
	def backupfiles_choosen(self, ret):
		config.plugins.configurationbackup.backupdirs.save()
		config.plugins.configurationbackup.save()
		config.save()

	def backupDone(self,retval = None):
		if retval is True:
			self.session.open(MessageBox, _("Backup done."), MessageBox.TYPE_INFO, timeout = 10)
		else:
			self.session.open(MessageBox, _("Backup failed."), MessageBox.TYPE_INFO, timeout = 10)

	def startRestore(self, ret = False):
		if (ret == True):
			self.exe = True
			self.session.open(RestoreScreen, runRestore = True)


######## Create MENULIST format #######################
def QuickMenuEntryComponent(name, description, long_description = None, width=540):
	pngname = name.replace(" ","_") 
	png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/icons/" + pngname + ".png")
	if png is None:
		png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/icons/default.png")

	return [
		_(name),
		MultiContentEntryText(pos=(120, 5), size=(width-120, 25), font=0, text = _(name)),
		MultiContentEntryText(pos=(120, 26), size=(width-120, 17), font=1, text = _(description)),
		MultiContentEntryPixmapAlphaTest(pos=(0, 5), size=(100, 40), png = png),
		_(long_description),
	]

def QuickSubMenuEntryComponent(name, description, long_description = None, width=540):
	return [
		_(name),
		MultiContentEntryText(pos=(50, 5), size=(width-10, 25), font=0, text = _(name)),
		MultiContentEntryText(pos=(50, 26), size=(width-10, 17), font=1, text = _(description)),
		_(long_description),
	]

class QuickMenuList(MenuList):
	def __init__(self, list, enableWrapAround=True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 20))
		self.l.setFont(1, gFont("Regular", 14))
		self.l.setItemHeight(50)

class QuickMenuSubList(MenuList):
	def __init__(self, sublist, enableWrapAround=True):
		MenuList.__init__(self, sublist, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 20))
		self.l.setFont(1, gFont("Regular", 14))
		self.l.setItemHeight(50)

class QuickMenuDevices(Screen):
	skin = """
		<screen name="QuickMenuDevices" position="center,center" size="840,525" title="Devices" flags="wfBorder">
		<widget source="devicelist" render="Listbox" position="30,46" size="780,450" font="Regular;16" scrollbarMode="showOnDemand" transparent="1" backgroundColorSelected="grey" foregroundColorSelected="black">
		<convert type="TemplatedMultiContent">
				{"template": [
				 MultiContentEntryText(pos = (90, 0), size = (600, 30), font=0, text = 0),
				 MultiContentEntryText(pos = (110, 30), size = (600, 50), font=1, flags = RT_VALIGN_TOP, text = 1),
				 MultiContentEntryPixmapAlphaBlend(pos = (0, 0), size = (80, 80), png = 2),
				],
				"fonts": [gFont("Regular", 24),gFont("Regular", 20)],
				"itemHeight": 85
				}
			</convert>
	</widget>
	<widget name="lab1" zPosition="2" position="126,92" size="600,40" font="Regular;22" halign="center" backgroundColor="black" transparent="1" />
	</screen> """

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Devices"))
		self['lab1'] = Label()
		self.devicelist = []
		self['devicelist'] = List(self.devicelist)

		self['actions'] = ActionMap(['WizardActions'], 
		{
			'back': self.close,
		})
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.updateList2)
		self.updateList()

	def updateList(self, result = None, retval = None, extra_args = None):
		scanning = _("Wait please while scanning for devices...")
		self['lab1'].setText(scanning)
		self.activityTimer.start(10)

	def updateList2(self):
		self.activityTimer.stop()
		self.devicelist = []
		list2 = []
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			if not search('sd[a-z][1-9]',device):
				continue
			if device in list2:
				continue
			self.buildMy_rec(device)
			list2.append(device)

		f.close()
		self['devicelist'].list = self.devicelist
		if len(self.devicelist) == 0:
			self['lab1'].setText(_("No Devices Found !!"))
		else:
			self['lab1'].hide()

	def buildMy_rec(self, device):
		try:
			if device.find('1') > 0:
				device2 = device.replace('1', '')
		except:
			device2 = ''
		try:
			if device.find('2') > 0:
				device2 = device.replace('2', '')
		except:
			device2 = ''
		try:
			if device.find('3') > 0:
				device2 = device.replace('3', '')
		except:
			device2 = ''
		try:
			if device.find('4') > 0:
				device2 = device.replace('4', '')
		except:
			device2 = ''
		devicetype = path.realpath('/sys/block/' + device2 + '/device')
		d2 = device
		name = 'USB: '
		mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/icons/dev_usbstick.png'
		model = file('/sys/block/' + device2 + '/device/model').read()
		model = str(model).replace('\n', '')
		des = ''
		if devicetype.find('/devices/pci') != -1:
			name = _("HARD DISK: ")
			mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/icons/dev_hdd.png'
		name = name + model

		from Components.Console import Console
		self.Console = Console()
		self.Console.ePopen("sfdisk -l /dev/sd? | grep swap | awk '{print $(NF-9)}' >/tmp/devices.tmp")
		sleep(0.5)
		f = open('/tmp/devices.tmp', 'r')
		swapdevices = f.read()
		f.close()
		swapdevices = swapdevices.replace('\n','')
		swapdevices = swapdevices.split('/')
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				d1 = parts[1]
				dtype = parts[2]
				rw = parts[3]
				break
				continue
			else:
				if device in swapdevices:
					parts = line.strip().split()
					d1 = _("None")
					dtype = 'swap'
					rw = _("None")
					break
					continue
				else:
					d1 = _("None")
					dtype = _("unavailable")
					rw = _("None")
		f.close()
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				size = int(parts[2])
				if ((size / 1024) / 1024) > 1:
					des = _("Size: ") + str((size / 1024) / 1024) + _("GB")
				else:
					des = _("Size: ") + str(size / 1024) + _("MB")
			else:
				try:
					size = file('/sys/block/' + device2 + '/' + device + '/size').read()
					size = str(size).replace('\n', '')
					size = int(size)
				except:
					size = 0
				if (((size / 2) / 1024) / 1024) > 1:
					des = _("Size: ") + str(((size / 2) / 1024) / 1024) + _("GB")
				else:
					des = _("Size: ") + str((size / 2) / 1024) + _("MB")
		f.close()
		if des != '':
			if rw.startswith('rw'):
				rw = ' R/W'
			elif rw.startswith('ro'):
				rw = ' R/O'
			else:
				rw = ""
			des += '\t' + _("Mount: ") + d1 + '\n' + _("Device: ") + ' /dev/' + device + '\t' + _("Type: ") + dtype + rw
			png = LoadPixmap(mypixmap)
			res = (name, des, png)
			self.devicelist.append(res)
