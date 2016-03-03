#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas
import pydre.core

metricsList = {}

# metrics defined here take a list of DriveData objects and return a single floating point value
def meanVelocity(regions, cutoff=0):
	total_vel = pandas.Series()
	for r in regions:
		data = r.data
		total_vel = total_vel.append(data[data.Velocity >= cutoff].Velocity)
	return total_vel.mean()

def steeringEntropy(regions,cutoff=0):
    out = []
    for i in range(0, len(regions)):
        df = pandas.DataFrame(regions[i].data)
        df = pandas.DataFrame(df, columns=("SimTime","Steer")) #drop other columns
        df = pandas.DataFrame.drop_duplicates(df.dropna(axis = [0,1], how='any')) #remove nans and drop duplicates

        #resample data
        minTime = df.SimTime.values.min()
        maxTime = df.SimTime.values.max()
        nsteps = math.floor((maxTime - minTime) / 0.0167)  #divide into 0.0167s increments
        regTime = np.linspace(minTime, maxTime, num=nsteps)
        rsSteer = np.interp(regTime, df.SimTime, df.Steer)
        resampdf = np.column_stack((regTime, rsSteer))
        resampdf = pandas.DataFrame(resampdf, columns=("simTime","rsSteerAngle")) #df

        #calculate predicted angle
        pAngle = (2.5 * df.Steer.values[3:,]) - (2 * df.Steer.values[2:-1,]) - (0.5 * df.Steer.values[1:-2,]);

        #calculate error
        error = df.Steer.values[3:,] - pAngle
        out.append(error)

    #concatenate out (list of np objects) into a single list
    error = np.stack(out)
    #90th percentile of error
    alpha = np.nanpercentile(error,90)

    #divide into 9 bins with edges: -5a,-2.5a,-a,a,2.5,5a
    binnedError = np.histogram(error, bins= [-10 * abs(alpha), -5 * abs(alpha), -2.5 * abs(alpha), -abs(alpha), -0.5 * abs(alpha), 0.5 * abs(alpha), abs(alpha), 2.5 * abs(alpha), 5 * abs(alpha), 10 * abs(alpha)])

    #calculate H
    binnedArr = np.asarray(binnedError[0])
    binnedArr = binnedArr.astype(float)

    #check out calc of p
    p = np.divide(binnedArr,np.sum(binnedArr))
    Hp = np.multiply(np.multiply(-1,p),(np.log(p)/np.log(9)))
    Hp = Hp[~np.isnan(Hp)]
    Hp = np.sum(Hp)

    return Hp

metricsList['meanVelocity'] = meanVelocity
metricsList['steeringEntropy'] = steeringEntropy
