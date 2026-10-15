"""解答の代表的な恒等式を独立に数値検算（標準ライブラリのみ）。"""
import cmath
import math
import random
from pathlib import Path
random.seed(20260928)
errors = {}
errors['Q3,Q4,Q7: amplitude, phase and complex coefficients'] = max(
    abs(a*math.sin(t)+b*math.cos(t)-2*((b-1j*a)/2*cmath.exp(1j*t)).real)
    for a,b,t in [(random.uniform(-5,5), random.uniform(-5,5), random.uniform(-10,10)) for _ in range(100)]
)
errors['Q3: atan2 phase convention'] = max(
    abs(a*math.sin(t)+b*math.cos(t)-math.hypot(a,b)*math.cos(t-math.atan2(a,b)))
    for a,b,t in [(random.uniform(-5,5), random.uniform(-5,5), random.uniform(-10,10)) for _ in range(100)]
)
for real in (True,False):
    periodic=[]; inverse=[]; conjugate=[]
    for n in (3,4,5,8,17):
        dt=.13
        x=[random.uniform(-2,2)+(0 if real else 1j*random.uniform(-2,2)) for _ in range(n)]
        def dft(l):
            return dt*sum(v*cmath.exp(-2j*math.pi*l*k/n) for k,v in enumerate(x))
        X=[dft(l) for l in range(n)]
        periodic += [abs(dft(l+n)-X[l]) for l in range(n)]
        inverse += [abs(sum(X[l]*cmath.exp(2j*math.pi*l*k/n) for l in range(n))/(n*dt)-x[k]) for k in range(n)]
        if real:
            conjugate += [abs(dft(n-2)-X[2].conjugate())]
    errors[f'Q11: periodicity, real={real}']=max(periodic)
    errors[f'Q14: inverse DFT, real={real}']=max(inverse)
    if real:
        errors['Q13: conjugate symmetry for real data']=max(conjugate)
errors['Q12: identical samples in diagram']=max(abs(math.cos(2*math.pi*k/8)-math.cos(2*math.pi*9*k/8)) for k in range(9))
for key,value in errors.items():
    assert value < 1e-11,(key,value)
report='\n'.join(f'{key}: maximum absolute error = {value:.3e}' for key,value in errors.items())+'\nAll checks passed (tolerance 1e-11).\n'
Path('verification/answers_numerical_checks.txt').write_text(report)
print(report)
