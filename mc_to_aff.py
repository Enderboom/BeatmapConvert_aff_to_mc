import json

#beat->[第X拍, 第Y个音符, 该拍共分割为Z个音符]->[X, Y, Z]

#将beat转化为统一单位,即用小数表示其为第几拍
def unit_beat(beat):
    return beat[0]+beat[1]/beat[2]

#将beat依据BPM转化为时间
def beat_to_time(beat, bpm):
    k = 60000/bpm
    if type(beat) == list:
        b = unit_beat(beat)
    else:
        b = beat
    return int(b*k)

#获取note处于的timing区间的序号
def get_sn(beat):
    sn = None
    for i in range(len(time_lst)):
        if beat < time_lst[i][0]:
            sn = i-1
            break
    if sn == None:
        sn = -1
    return sn

#获取原谱面文件内容
while 1:
    mc_name = input('请输入Malody谱面文件名(不需要后缀)>>>')+'.mc'
    try:
        with open(mc_name, 'r') as f:
            mc_chart = json.load(f)
            break
    except FileNotFoundError:
        print('文件名不存在!请重新输入')

#读取mc谱面内容
mc_timing = mc_chart['time']
mc_note = mc_chart['note']

#基本信息初始化
base_bpm = mc_timing[0]['bpm']
AudioOffSet = 0
for note_info in mc_note:
    if 'offset' in note_info:
        AudioOffSet = int(-note_info["offset"])
aff_head = f'AudioOffset:{AudioOffSet}\n-\n'
aff_timing = ''
aff_body = ''

#转换timing
time_lst = [[unit_beat(mc_timing[0]['beat']), base_bpm, beat_to_time(mc_timing[0]['beat'], base_bpm)]]
if len(mc_timing) > 1:
    i = 0
    for timing in mc_timing:
        beat = unit_beat(timing['beat'])
        bpm = timing['bpm']
        dt_beat = beat-time_lst[i][0]
        time = beat_to_time(dt_beat, time_lst[i][1])+time_lst[i][2]
        time_lst.append([beat, bpm, time])
        aff_timing += f'timing({time},{round(bpm, 2)},4.00);\n'
        i += 1

#转换note
for note in mc_note:
    beat = unit_beat(note['beat'])
    sn = get_sn(beat)
    dt_beat = beat-time_lst[sn][0]
    st = beat_to_time(dt_beat, time_lst[sn][1])+time_lst[sn][2]
    #Hold
    if 'endbeat' in note:
        column = note['column']+1
        endbeat = unit_beat(note['endbeat'])
        sn = get_sn(endbeat)
        dt_beat = endbeat-time_lst[sn][0]
        ed = beat_to_time(dt_beat, time_lst[sn][1])+time_lst[sn][2]
        aff_body += f'hold({st},{ed},{column});\n'
    #Tap
    elif 'column' in note:
        column = note['column']+1
        aff_body += f'({st},{column});\n'

#写入aff
aff = aff_head+aff_timing+aff_body
with open('base.aff', 'w') as f:
    f.write(aff)