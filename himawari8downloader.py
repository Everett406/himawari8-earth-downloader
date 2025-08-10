import sys
import json
import requests
import os
from PIL import Image
from io import BytesIO
from datetime import datetime
from dateutil import tz

conf ={
    'last_refresh_url': 'https://himawari8-dl.nict.go.jp/himawari8/img/D531106/latest.json',  # latest photo
    'img_url_pattern': 'https://himawari8-dl.nict.go.jp/himawari8/img/D531106/%id/550/%s_%i_%i.png',    # scale, time, row, col
    'scale': 4,     # 1, 2, 4, 8, 16, 20.  Width and height are both 550*scale
}


# Convert time
def utf2local(utc):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone)


def download(args):
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    scale = args['scale']
    png = Image.new('RGB', (550*scale, 550*scale))
    
    for row in range(scale):
        for col in range(scale):
            print('Downloading %i of %i ...' % (row*scale + col + 1, scale*scale))
            strtime = args['time'].strftime("%Y/%m/%d/%H%M%S")
            url = conf['img_url_pattern'] % (args['scale'], strtime, row, col)
            
            try:
                r = requests.get(url, verify=False, timeout=30)
                r.raise_for_status()
                tile = Image.open(BytesIO(r.content))
                png.paste(tile, (550 * row, 550 * col, 550 * (row + 1), 550 * (col + 1)))
            except Exception as e:
                print(f"Error downloading tile ({row}, {col}): {e}")
                # Create a black tile as fallback
                tile = Image.new('RGB', (550, 550), color='black')
                png.paste(tile, (550 * row, 550 * col, 550 * (row + 1), 550 * (col + 1)))
    
    # 处理输出路径
    if 'output_dir' in args and args['output_dir']:
        output_dir = args['output_dir']
        # 如果目录不存在则创建
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    else:
        output_dir = os.getcwd()
    
    if 'fout' in args:
        filename = args['fout']
    else:
        filename = "%s.png" % utf2local(args['time']).strftime("%Y%m%d%H%M%S")
    
    # 组合完整路径
    fpath = os.path.join(output_dir, filename)
    
    print('Download over, save to file %s' % fpath)
    png.save(fpath, "PNG")


def get_last_time():
    try:
        r = requests.get(conf['last_refresh_url'], verify=False, timeout=30)
        r.raise_for_status()
        resp = json.loads(r.text)
        last_refresh_time = datetime.strptime(resp['date'], '%Y-%m-%d %H:%M:%S')
        return last_refresh_time
    except Exception as e:
        print(f"Error getting last time: {e}")
        # Fallback to current time rounded to 10 minutes
        now = datetime.utcnow()
        now = now.replace(minute=(now.minute // 10) * 10, second=0, microsecond=0)
        return now


def get_last_image(fout=None, scale=1, output_dir=None):
    print('output[%s] scale[%i] dir[%s]' %(fout, scale, output_dir))
    last_refresh_time = get_last_time()
    args = {'time': last_refresh_time}
    args['scale'] = scale
    if fout is not None:
        args['fout'] = fout
    if output_dir is not None:
        args['output_dir'] = output_dir
    download(args)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        get_last_image()
    elif len(sys.argv) == 2:
        get_last_image(fout=sys.argv[1])
    elif len(sys.argv) == 3:
        # 检查第三个参数是否是数字（scale）还是路径
        try:
            scale = int(sys.argv[2])
            get_last_image(fout=sys.argv[1], scale=scale)
        except ValueError:
            get_last_image(fout=sys.argv[1], output_dir=sys.argv[2])
    elif len(sys.argv) == 4:
        get_last_image(fout=sys.argv[1], scale=int(sys.argv[2]), output_dir=sys.argv[3])
    else:
        print("用法:")
        print("  python himawari8downloader.py")
        print("  python himawari8downloader.py [输出文件名]")
        print("  python himawari8downloader.py [输出文件名] [分辨率倍数]")
        print("  python himawari8downloader.py [输出文件名] [分辨率倍数] [输出目录]")
        print("  python himawari8downloader.py [输出文件名] [输出目录]")
        print("分辨率倍数: 1, 2, 4, 8, 16, 20")
