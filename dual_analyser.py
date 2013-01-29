import cwiid
import time
from numpy import * #Import matrix libraries
from pylab import *
import subprocess # Used to create ffmpeg video capture subprocess
import os # Used to kill ffmpeg subprocess

print '\nPlease press 1+2 on your Wiimotes now...'

# To find the remotes, type the following in a the terminal:
#   hcitool scan
# Then enter relevant addresses into the commands below
wm1 = cwiid.Wiimote("00:21:BD:02:51:BB") #Original
wm2 = cwiid.Wiimote("00:22:4C:8F:80:29") #Personal

print "Wiimotes activiated!\n"
print "Please wait for the Wiimotes to calibrate..."

wm1.enable(cwiid.FLAG_MESG_IFC)
wm2.enable(cwiid.FLAG_MESG_IFC)

wm1.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_BTN # Enable Accelerometer and Button Reporting
wm2.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_BTN

wm1.led = 1 # Set Wiimote LEDs
wm2.led = 2

time.sleep(1)

# Setup Constants
i = 0 # Counter 
j = 0
t=[0] # Used for time appending
ax1=[0] # Accelerometer values
ay1=[0]
az1=[0]
ax2=[0] 
ay2=[0]
az2=[0]
rec_flg =0 # Record state
flg=True # Active state
tprev=0
cal_flg = 1 # Calibration state
cal_cnt = 0
ax1_cal=[0] # Calibration values
ay1_cal=[0]
az1_cal=[0]
ax2_cal=[0]
ay2_cal=[0]
az2_cal=[0]
ax1c = 0 # Calibration averages
ay1c = 0
az1c = 0
ax2c = 0
ay2c = 0
az2c = 0
st = time.strftime("%y%m%d_%H%M%S")

# Begin video recording
subprocess.Popen(['python', 'echo.py'], stderr=subprocess.STDOUT,stdout = subprocess.PIPE )

while flg==True:    # While Wiimote set to record
    time.sleep(0.01)
    
    messages1 = wm1.get_mesg()   # Get Wiimote Messages
    for mesg in messages1:   # Loop through Wiimote Messages
        if mesg[0] == cwiid.MESG_ACC: # If an accelerometer message
            if rec_flg == 1:    # Check if set to record
                
                # Record Time
                if i == 0:
		    print "Recording started!"
                i=i+1
                tm = time.time()
                if i > 1:
                    t.append(tm-tprev+t[i-1])
                    tprev = tm
                else:
                    tprev = tm
                    t.append(0.01)
                
                # Record Acceleration Data
                ax1.append(mesg[1][cwiid.X]-ax1c)
                ay1.append(mesg[1][cwiid.Y]-ay1c)
                az1.append(mesg[1][cwiid.Z]-az1c)
            
            # Record Calibration Data
            elif cal_flg == 1:
                cal_cnt = cal_cnt+1
                ax1_cal.append(mesg[1][cwiid.X])
                ay1_cal.append(mesg[1][cwiid.Y])
                az1_cal.append(mesg[1][cwiid.Z])
                if cal_cnt > 100:
                    ax1c = mean(ax1_cal)
                    ay1c = mean(ay1_cal)
                    az1c = mean(az1_cal)
        elif mesg[0] == cwiid.MESG_BTN:  # If a Wiimote button message
            if mesg[1] & cwiid.BTN_PLUS:    # Start recording if "+" button pressed
                rec_flg = 1
            elif mesg[1] & cwiid.BTN_MINUS: # Stop recording "-" button pressed
                flg=False
                break
        break       
    
    messages2 = wm2.get_mesg()
    for mesg in messages2:   # Loop through Wiimote Messages
        if mesg[0] == cwiid.MESG_ACC: # If an accelerometer message
            if rec_flg == 1:    # Check if set to record
                # Record Acceleration Data
                ax2.append(mesg[1][cwiid.X]-ax2c)
                ay2.append(mesg[1][cwiid.Y]-ay2c)
                az2.append(mesg[1][cwiid.Z]-az2c)
            
            # Record Calibration Data
            elif cal_flg == 1:
                ax2_cal.append(mesg[1][cwiid.X])
                ay2_cal.append(mesg[1][cwiid.Y])
                az2_cal.append(mesg[1][cwiid.Z])
                if cal_cnt > 100:
                    cal_flg=0
                    ax2c = mean(ax2_cal)
                    ay2c = mean(ay2_cal)
                    az2c = mean(az2_cal)
                    print "Wiimotes calibrated!\n"
		    print "Please press + to start recording and - to stop recording..."

        elif mesg[0] == cwiid.MESG_BTN:  # If a Wiimote button message
            if mesg[1] & cwiid.BTN_PLUS:    # Start recording if "+" button pressed
                rec_flg = 1
            elif mesg[1] & cwiid.BTN_MINUS: # Stop recording if "-" button pressed
                flg=False
                break
            
print "Recording finished!\n"

ax1m=[0] # Axis means
ay1m=[0]
az1m=[0]
as1m=[0]
ax2m=[0] # Axis means
ay2m=[0]
az2m=[0]
as2m=[0]
tm=[0]
avm=[0]
v=3
mcnt=0 # Mean count
maxa1=0
maxa2=0
tota1=0
tota2=0

os.system("killall ffmpeg") # Stop video recording
file = open("%s_data1.txt" % (st), "w") # Wipe the data files
file = open("%s_data2.txt" % (st), "w") 

# Smooth and analyse the data
for i in arange(1,len(ax1),v):   # Take the average of "v" points
    mcnt=mcnt+1
    if i+v > len(ax1): break
    ax1m.append(mean(ax1[i:i+v])) # Fix array lengths
    ay1m.append(mean(ay1[i:i+v]))
    az1m.append(mean(az1[i:i+v]))
    as1m.append(mean(az1[i:i+v]))
    ax2m.append(mean(ax2[i:i+v])) 
    ay2m.append(mean(ay2[i:i+v]))
    az2m.append(mean(az2[i:i+v]))
    as2m.append(mean(az2[i:i+v]))
    tm.append(mean(t[i:i+v]))
    
    # Calculate absolute forces
    as1m[mcnt] = abs(ax1m[mcnt]) + abs(ay1m[mcnt]) + abs(az1m[mcnt]) 
    as2m[mcnt] = abs(ax2m[mcnt]) + abs(ay2m[mcnt]) + abs(az2m[mcnt])
    if as1m[mcnt] > maxa1: # Find Max Accelerations
        maxa1 = as1m[mcnt]
    if as2m[mcnt] > maxa2: 
        maxa2 = as2m[mcnt] 
    tota1 = as1m[mcnt]+tota1 # Find Total Acceletations
    tota2 = as2m[mcnt]+tota2 
    
    file = open("%s_data1.txt" % (st), "a") # Open the date file for appending
    data_str = '%f	%f	%f	%f	%f\n' % (tm[mcnt],ax1m[mcnt],ay1m[mcnt],az1m[mcnt],as1m[mcnt]) # Create data string
    file.write(data_str) # Write data string to file
    file.close()

    file = open("%s_data2.txt" % (st), "a") # Open the date file for appending
    data_str = '%f	%f	%f	%f	%f\n' % (tm[mcnt],ax2m[mcnt],ay2m[mcnt],az2m[mcnt],as2m[mcnt]) # Create data string
    file.write(data_str) # Write data string to file
    file.close()
    
print "Maximum acceleration on Wiimote 1 is: %f" % maxa1
print "Maximum acceleration on Wiimote 2 is: %f\n" % maxa2
print "Total acceleration on Wiimote 1 is: %f" % tota1
print "Total acceleration on Wiimote 2 is: %f\n" % tota2

os.system("gnome-open %s_video.mpg" % st) # Show recorded video

#Create Plots
subplot(5,2,1) # Remote 1 Plots
plot(tm,ax1m,'r')   # Acceleration Plots
xlabel('time (s)')
ylabel('X-axis Accel.')
subplot(5,2,3)
plot(tm,ay1m,'b')   
xlabel('time (s)')
ylabel('Y-axis Accel.')
subplot(5,2,5)
plot(tm,az1m,'k')  
xlabel('time (s)')
ylabel('Z-axis Accel.')
subplot(5,2,7)
plot(tm,ax1m,'r')   # Overlayed Acceleration Plot
plot(tm,ay1m,'b')   
plot(tm,az1m,'k')   
xlabel('time (s)')
ylabel('XYZ Accel.')
subplot(5,2,9)
plot(tm,as1m,'g')   # Absolute Acceleration Plot
xlabel('time (s)')
ylabel('Total Accel.')

subplot(5,2,2) # Remote 2 Plots
plot(tm,ax2m,'r')   # Acceleration Plots
xlabel('time (s)')
ylabel('X-axis Accel.')
subplot(5,2,4)
plot(tm,ay2m,'b')   
xlabel('time (s)')
ylabel('Y-axis Accel.')
subplot(5,2,6)
plot(tm,az2m,'k')  
xlabel('time (s)')
ylabel('Z-axis Accel.')
subplot(5,2,8)
plot(tm,ax2m,'r')   # Overlayed Acceleration Plot
plot(tm,ay2m,'b')   
plot(tm,az2m,'k')   
xlabel('time (s)')
ylabel('XYZ Accel.')
subplot(5,2,10)
plot(tm,as2m,'g')   # Absolute Acceleration Plot
xlabel('time (s)')
ylabel('Total Accel.')
savefig(st, facecolor='w', edgecolor='w',
        orientation='landscape', papertype=None, format=None,
        transparent=False, bbox_inches='tight')
show()
