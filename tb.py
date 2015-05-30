import numpy as np
np.random.seed(4)

def main():
    d = scrape_ac_transit()
    d = remove_east(d)
    write_geojson(d)


def remove_east(d):
    return {k:v for k,v in d.iteritems() if not('east' in k)}


def write_geojson(d):
    f = open('transbay.geojson','w')
    f.write('{ "type": "FeatureCollection","features": [')
    c=0
    for bus_line in sorted(d.keys()):
        positions = d[bus_line]
        f.write(one_linestring(bus_line, positions, color=random_hex_color()))
        c += 1
        if (c<len(d.keys())): f.write(',')
    f.write(']}')
    f.close()
            

def one_linestring(bus_line, positions, color = 'blue'):
    output = '{ "type": "Feature","geometry": {"type": "LineString","coordinates": ['
    c=0
    for lat,lon in positions:
        output = output + '[%0.9f, %0.9f]'%(lon, lat)
        c+=1
        if c<len(positions): output = output + ','
    output = output + ']}, "properties": {"title": "%s", "description": "%s","stroke":"%s","stroke-width":"5"}}'%(bus_line, bus_line, color)
    return output

def scrape_ac_transit():
    '''
    returns a dictionary.
    keys are bus lines, like 'B' or 'FS'.
    values are lists of [lat,lon] pairs (float).
    '''
    import urllib2
    address = 'http://www.actransit.org/rider-info/stops/transbay/'
    html = urllib2.urlopen(address).readlines()
    output = {}
    direction_dict = {+1:'_west', -1:'_east'}
    direction=-1
    bus_line = 'x'
    for line in html:

        if 'span id=' in line:
            bus_line=line.split('span id=')[1].split('"')[1]
            output[bus_line+'_west'] = []
            output[bus_line+'_east'] = []
            direction=-1
            continue

        if '<td' in line:
            direction *= -1
            this_bus_line = bus_line+direction_dict[direction]
            if this_bus_line=='LC_west': this_bus_line='LC_east'
            if this_bus_line=='NX1_west': this_bus_line='NX1_east'
            if this_bus_line=='NX2_west': this_bus_line='NX2_east'
            if this_bus_line=='NXC_west': this_bus_line='NXC_east'
            continue

        if 'http://maps.google.com/maps?q=@' in line:
            for thing in line.split('http://maps.google.com/maps?q=@'):
                tmp=thing.split('&')[0]
                if '<p>' in tmp: continue
                if 'span' in tmp: continue
                lat, lon = tmp.split(',')
                output[this_bus_line].append([float(lat), float(lon)])
            continue

    for k,v in output.iteritems():
        output[k] = np.array(v)
        if 'west' in k: output[k] = output[k][0:-1]
        if 'east' in k: output[k] = output[k][1:]
    return output
        



def random_hex_color():
    r,g,b = np.random.randint(50,200,3)
    return '#%02X%02X%02X' % (r,g,b)



