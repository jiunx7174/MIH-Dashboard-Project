def GetDrillingActivity(ConnectionWeight,woba,rpm,stppress,Hookload):
    if(woba>0 and rpm>10 and stppress>100 and Hookload>ConnectionWeight):
        SubActivity_Label = "Rotary Drilling"
        if(woba>0 and rpm<10 and stppress>100 and Hookload>ConnectionWeight):
            SubActivity_Label = "Slide Drilling"
            if(woba==0 and rpm>10 and stppress>100 and Hookload>ConnectionWeight):
                SubActivity_Label = "Reaming"
                if(woba==0 and rpm==0 and stppress>100 and Hookload>ConnectionWeight):
                    SubActivity_Label = "Wash Up/Down"
                    
                    if(woba==0 and rpm==0 and stppress<50 and Hookload<ConnectionWeight):
                        SubActivity_Label = "Connection"
                    else:
                        SubActivity_Label = "Look and define"

    return SubActivity_Label

def GetTrippingActivity():

    if((isBitDepthMoving and hklda>Hookload and rpm==0 and mudflowing>10)):

        SubActivity_Label = "Wash Up/Down"
    elif((isBitDepthMoving and hklda>Hookload and rpm>10 and stppress>100 and mudflowing>10)):
        SubActivity_Label = "Reaming"
    elif((isBitDepthMoving and hklda>Hookload and rpm<10 and stppress<100 and mudflowing<50)):
        SubActivity_Label = "Moving"
    elif((isBitDepthMoving and hklda>Hookload and mudflowing>10)):
        SubActivity_Label = "Circulation"
    elif((mudflowing<10 and rpm<10 and hklda<Hookload)):
        SubActivity_Label = "Connection"
    elif((isBitDepthMoving and mudflowing<10 and rpm<10 and hklda>Hookload)):
        SubActivity_Label = "Stationary"
    else:
        SubActivity_Label = "Check"




def GetDrillingActivity_v2():
    if(woba>0 and rpm>10 and stppress>100 and hklda>ConnectionWeight):
        SubActivity_Label = "Rotary Drilling"
    elif(woba>0 and rpm<10 and stppress>100 and hklda>ConnectionWeight):
        SubActivity_Label = "Slide Drilling"
    elif(woba==0 and rpm>10 and stppress>100 and hklda>ConnectionWeight):
        SubActivity_Label = "Reaming"
    elif(woba==0 and rpm==0 and stppress>100 and hklda>ConnectionWeight):
        SubActivity_Label = "Wash Up/Down"
    # elif(woba=0 and rpm=0 and stppress<50)elif(hklda<ConnectionWeight and "Connection" and "Look and define"))))))
    elif(woba==0 and rpm==0 and stppress<50):
        if(hklda<ConnectionWeight):
            SubActivity_Label = "Connection"
        else:
            SubActivity_Label="Look and define"
    else:
        SubActivity_Label = "FALSE"





# Hookload = Hookload
# E3 = bitdepth_current
# E4 = bitdepth_future

# g3 = hklda
# h3 = rpm
# i3 = stppress 
# j3 = mudflowing

# I3 = woba
# K3 = rpm
# L3 = stppress
# N3 = Hookload
