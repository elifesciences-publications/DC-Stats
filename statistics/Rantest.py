#!/usr/bin python

'rantest.py -- RANDOMISATION TEST FOR TWO SAMPLES.\
               Converted from FORTRAN version RANTEST.FOR'

import math
import random

__author__="remis"
__date__ ="$01-May-2009 17:42:28$"

class Rantest(object):

    introd = '\n RANTEST: performs a randomisation test to compare two \
independent samples. According to the null hypothesis\n \
of no-difference, each outcome would have been the same \
regardless of which group the individual happened to\n \
be allocated. Therefore all N=n1+n2 observations are \
pooled and, as in the actual experiment, divided at random\n \
into groups of size n1 and n2. The fraction \
of randomisations that gives rise to a difference between the groups\n \
at least as large as that observed \
gives the P value.\
\n In the binomial case, in which the measurement is the \
fraction of ''successes'' in each sample (say r1 out of n1, and\n \
r2 out of n2) a ''success'' is given a \
score of 1, ''failure'' = 0.\n'


    dict = {}

    def betacf(self, A, B, X):
        'Used by betai(). Evaluates continued fraction for incomplete beta \
        function by modified Lentz_s method. \
        Adopted from Numwerical Recipes in Fortran77: The Art Of Scientific \
        Computing by Press et al 1997. '

        ITMAX = 100
        EPS = 3.E-7
        AM = 1.0
        BM = 1.0
        AZ = 1.0
        QAB = A + B
        QAP = A + 1.0
        QAM = A - 1.0
        BZ = 1.0 - QAB * X / QAP
        for m in range(1, ITMAX+1):
            EM = m
            TEM = EM + EM
            D = EM * (B -m) * X / ((QAM + TEM) * (A + TEM))
            AP = AZ + D * AM
            BP = BZ + D * BM
            D = -(A + EM) * (QAB + EM) * X / ((A + TEM) * (QAP + TEM))
            APP = AP + D * AZ
            BPP = BP + D * BZ
            AOLD = AZ
            AM = AP / BPP
            BM = BP / BPP
            AZ = APP / BPP
            BZ = 1.0
            #if math.fabs(AZ - AOLD) > EPS * math.fabs(AZ):
            #    print 'A or B too big, or ITMAX too small'
        BETACF = AZ
        return BETACF

    def gammln(self, XX):
        'Returns natural logaritm of gama function. \
        Adopted from Numwerical Recipes in Fortran77: The Art Of Scientific \
        Computing by Press et al 1997. '

        COF = [76.18009173e0, -86.50532033e0, 24.01409822e0, -1.231739516e0, .120858003e-2, -.536382e-5]
        STP = 2.50662827465e0
        ONE = 1.0e0
        HALF = 0.5e0
        FPF = 5.5e0
        X= XX - ONE
        TMP = X + FPF
        TMP = (X + HALF) * math.log(TMP) - TMP
        SER = ONE
        for j in range(0, 6):
            X = X + ONE
            SER = SER + COF[j] / X
        GAMMLN = TMP + math.log(STP * SER)
        return GAMMLN

    def betai(self, A, B, X):
        'Incomplete beta function. \
        Adopted from Numwerical Recipes in Fortran77: The Art Of Scientific \
        Computing by Press et al 1997. '

        if (X < 0) or (X > 1): print 'bad argument X in BETAI'
        if (X == 0) or (X == 1):
            BT=0.0
        else:
            BT = math.exp(self.gammln(A + B) - self.gammln(A) - self.gammln(B) + A * math.log(X) + B * math.log(1.0 - X))
        if X < (A + 1.0) / (A + B + 2.0):
            BETAI = BT * self.betacf(A, B, X) / A
            return BETAI
        else:
            BETAI = 1.0 - BT * self.betacf(B, A, 1.0 - X) / B
            return BETAI

    def meanvar(self, X):

        n = len(X)
        sumx = X[0]
        sumxx = 0.0
        for i in range(1, n):
            sumx = sumx + X[i]
            sumxx = sumxx + ((i+1) * X[i] - sumx)**2 / float((i+1)*i)
        xbar = sumx / float(n)
        varx = sumxx /float(n - 1)
        sdx = math.sqrt(varx)
        sex = sdx / math.sqrt(n)

        return xbar, varx, sdx, sex

    def tTestBinomial(self, n1, n2, ir1, ir2):
        ''

        #Use Gaussian approx to do 2 sample t test
        p1 = float(ir1) / float(n1)
        p2 = float(ir2) / float(n2)
        ppool = float(ir1 + ir2) / float(n1 + n2)
        sd1 = math.sqrt(p1 * (1.0 - p1) / float(n1))
        sd2 = math.sqrt(p2 * (1.0 - p2) / float(n2))
        sd1p = math.sqrt(ppool * (1.0 - ppool) / float(n1))
        sd2p = math.sqrt(ppool * (1.0 - ppool) / float(n2))
        sdiff = math.sqrt(sd1p * sd1p + sd2p * sd2p)

        tval = math.fabs(p1 - p2) / sdiff
        df = 100000    # to get Gaussian
        x = df / (df + tval * tval)
        P = self.betai(0.5 * df, 0.5, x)

        self.dict['p1'] = p1
        self.dict['p2'] = p2
        self.dict['sd1'] = sd1
        self.dict['sd2'] = sd2
        self.dict['tval'] = tval
        self.dict['P'] = P

        self.dict['ir1'] = ir1
        self.dict['ir2'] = ir2
        self.dict['n1'] = n1
        self.dict['n2'] = n2

    def doRantestBinomial(self, n1, n2, ir1, ir2, nran):

        p1 = float(ir1) / float(n1)
        p2 = float(ir2) / float(n2)
        dobs = p1 - p2

        allobs = []
        for i in range(0, n1):
            if i < ir1:
                allobs.append(1.0)
            else:
                allobs.append(0.0)
        for i in range(0, n2):
            if i < ir2:
                allobs.append(1.0)
            else:
                allobs.append(0.0)

        ng1 = 0
        nl1 = 0
        na1 = 0
        ne1 = 0
        ne2 = 0

        randiff = []

        for n in range(0, nran):

            # Randomisation happens here
            iran = range(0, n1 + n2)
            random.shuffle(iran)

            is2 = 0.0
            for i in range(0, n2):
                j = n1 + n2 - i - 1
                is2 = is2 + allobs[iran[j]]
            is1 = ir1 + ir2 - is2
            xb1 = is1 / float(n1)    # mean
            yb1 = is2 / float(n2)    # mean
            dran = xb1 - yb1
            randiff.append(float(is1))

            # icrit=2
            if dran >= dobs: ng1 = ng1 + 1
            if dran <= dobs: nl1 = nl1 + 1
            if dran == dobs: ne1 = ne1 + 1
            if math.fabs(dran) >= math.fabs(dobs): na1 = na1 + 1
            if math.fabs(dran) == math.fabs(dobs): ne2 = ne2 + 1

        self.dict['pg1'] = float(ng1) / float(nran)
        self.dict['pl1'] = float(nl1) / float(nran)
        self.dict['pe1'] = float(ne1) / float(nran)
        self.dict['pa1'] = float(na1) / float(nran)
        self.dict['pe2'] = float(ne2) / float(nran)

        self.dict['dobs'] = dobs    # check, also used for student test
        self.dict['randiff'] = randiff

        self.dict['ng1'] = ng1
        self.dict['nl1'] = nl1
        self.dict['na1'] = na1
        self.dict['ne1'] = ne1
        self.dict['ne2'] = ne2
        self.dict['nran'] = nran

    def data_statistics(self):

        xobs = self.dict['xobs']
        yobs = self.dict['yobs']

        nx = len(xobs)
        ny = len(yobs)
        
        # calculate mean and variance of nx and ny
        xbar, varx, sdx, sex = self.meanvar(xobs)
        ybar, vary, sdy, sey = self.meanvar(yobs)
        
        D = []
        dbar = 0.0
        vard = 0.0
        sdd = 0.0
        sed = 0.0

        if nx == ny:
            for i in range(0, nx):
                D.append(xobs[i] - yobs[i])    # differences for paired test
            dbar, vard, sdd, sed = self.meanvar(D)

        self.dict['xbar'] = xbar
        self.dict['varx'] = varx
        self.dict['sdx'] = sdx
        self.dict['sex'] = sex
        self.dict['ybar'] = ybar
        self.dict['vary'] = vary
        self.dict['sdy'] = sdy
        self.dict['sey'] = sey
        self.dict['dbar'] = dbar
        self.dict['vard'] = vard
        self.dict['sdd'] = sdd
        self.dict['sed'] = sed

    def tTestContinuous(self, paired):

        xobs = self.dict['xobs']
        yobs = self.dict['yobs']
        sdd = self.dict['sdd']
        dbar = self.dict['dbar']
        sdx = self.dict['sdx']
        sdy = self.dict['sdy']
        xbar = self.dict['xbar']
        ybar = self.dict['ybar']

        nx = len(xobs)
        ny = len(yobs)
        df = 1
        adiff = 0.0
        sdiff = 0.0
        sdbar = 0.0

        # And do a 2-sample t-test
        if paired:
            df = nx - 1
            sdbar = sdd / math.sqrt(ny)
            tval = dbar / sdbar
            x = df / (df + tval * tval)
            P = self.betai(0.5 * df, 0.5, x)
            
        else:    # if not paired
            df = nx + ny - 2
            s = (sdx * sdx * (nx-1) + sdy * sdy * (ny-1)) / df
            sdiff = math.sqrt(s * (1.0 / nx + 1.0 / ny))
            adiff = math.fabs(xbar - ybar)
            tval = adiff / sdiff
            x = df / (df + tval * tval)
            P = self.betai(0.5 * df, 0.5, x)

        self.dict['P'] = P
        self.dict['tval'] = tval
        self.dict['df'] = df
        self.dict['adiff'] = adiff
        self.dict['sdiff'] = sdiff
        self.dict['sdbar'] = sdbar

    def setContinuousData(self, in_data, jset):

        self.dict['nx'] = in_data[(jset-1)*7+1]
        self.dict['ny'] = in_data[(jset-1)*7+2]
        self.dict['titled'] = in_data[(jset-1)*7+3]
        self.dict['titlex'] = in_data[(jset-1)*7+4]
        self.dict['titley'] = in_data[(jset-1)*7+5]
        self.dict['xobs'] = in_data[(jset-1)*7+6]
        self.dict['yobs'] = in_data[(jset-1)*7+7]

    def doRantestContinuous(self, paired, nran):

        xobs = self.dict['xobs']
        yobs = self.dict['yobs']

        nx = len(xobs)
        ny = len(yobs)

        D = []
        if nx == ny:
            for i in range(0, nx):
                D.append(xobs[i] - yobs[i])    # differences for paired test

        dobs = 0.0
        allobs = []
        randiff = []
        # for randomisation
        ng1 = 0
        nl1 = 0
        na1 = 0
        ne1 = 0
        ne2 = 0

        if paired:
            dobs = self.dict['dbar']    # observed mean difference
            # put absolute differences into allobs() for paired test
            for i in range(0, nx):
                allobs.append(math.fabs(D[i]))
            # start randomisation
            for n in range(0, nran):
                sd = 0.0
                for i in range(0, nx):
                    u = random.random()
                    if u < 0.5:
                        sd = sd - allobs[i]
                    else:
                        sd = sd + allobs[i]
                dran = sd / float(nx)    # mean difference
                randiff.append(dran)
                if dran >= dobs: ng1 = ng1 + 1
                if dran <= dobs: nl1 = nl1 + 1
                if math.fabs(dran) >= math.fabs(dobs): na1 = na1 + 1
                if dran == dobs: ne1 = ne1 + 1
                if math.fabs(dran) == math.fabs(dobs): ne2 = ne2 + 1
                # end of if(paired)

        else:    # if not paired

            dobs = self.dict['xbar'] - self.dict['ybar']
            # Put all obs into one array for unpaired test
            k = 0
            stot = 0.0
            for i in range(0, nx):
                k = k + 1
                stot = stot + xobs[i]
                allobs.append(xobs[i])
            for i in range(0, ny):
                k = k + 1
                stot = stot + yobs[i]
                allobs.append(yobs[i])

            # start randomisation
            for n in range(0, nran):
                iran = range(0,(nx + ny))
                random.shuffle(iran)
                sy = 0.0
                for i in range(0, ny):
                    j = nx + ny - i - 1
                    sy = sy + allobs[iran[j]]

                sx = stot - sy
                xb1 = sx / float(nx)    # mean
                yb1 = sy / float(ny)    # mean
                dran = xb1 - yb1

                randiff.append(dran)
                if dran >= dobs: ng1 = ng1 + 1
                if dran <= dobs: nl1 = nl1 + 1
                if math.fabs(dran) >= math.fabs(dobs): na1 = na1 + 1
                if dran == dobs: ne1 = ne1 + 1
                if math.fabs(dran) == math.fabs(dobs): ne2 = ne2 + 1

        self.dict['nran'] = nran
        self.dict['dobs'] = dobs
        self.dict['randiff'] = randiff

        self.dict['pg1'] = ng1 / float(nran)
        self.dict['pl1'] = nl1 / float(nran)
        self.dict['pe1'] = ne1 / float(nran)
        self.dict['pa1'] = na1 / float(nran)
        self.dict['pe2'] = ne2 / float(nran)
        self.dict['ng1'] = ng1
        self.dict['nl1'] = nl1
        self.dict['na1'] = na1
        self.dict['ne1'] = ne1
        self.dict['ne2'] = ne2

    def __init__(self):
        pass

if __name__ == "__main__":

    print introd