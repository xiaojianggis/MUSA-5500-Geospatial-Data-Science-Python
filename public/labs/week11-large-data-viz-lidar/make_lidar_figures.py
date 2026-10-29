"""Rebuild the tutorial's schematic LiDAR diagrams (not measured data)."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
from scipy.ndimage import median_filter

OUT = Path(__file__).parent / 'imgs'
OUT.mkdir(exist_ok=True)
INK, BLUE, GREEN, ORANGE = '#17324d', '#1268a2', '#15836b', '#d66522'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12,
                     'text.color': INK, 'axes.labelcolor': INK, 'axes.titleweight': 'bold',
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.facecolor': 'white', 'savefig.facecolor': 'white'})

def save(fig, name):
    fig.savefig(OUT / f'{name}.png', dpi=170, bbox_inches='tight')
    fig.savefig(OUT / f'{name}.svg', bbox_inches='tight')
    plt.close(fig)

def arrow(ax, a, b, color=BLUE, **kwargs):
    ax.annotate('', xy=b, xytext=a, arrowprops=dict(arrowstyle='-|>', lw=2.3,color=color,**kwargs))

# 1: Pulse travel time and positioning.
fig, ax = plt.subplots(figsize=(11,5.6)); ax.set(xlim=(0,11),ylim=(0,6));ax.axis('off')
ax.set_title('1  Measure travel time → calculate distance → locate a point',loc='left',pad=20)
ax.plot([.5,10.5],[.65,.65],color=GREEN,lw=3)
ax.add_patch(Rectangle((4.4,.65),2,1.3,facecolor='#dfe9ed',edgecolor=INK))
ax.text(5.4,1.2,'Roof',ha='center')
ax.add_patch(Polygon([[4.3,4.9],[6.8,4.9],[6.2,5.2],[5.4,5.2],[4.7,5.6],[4.5,5.55],[4.8,5.15],[4.3,5.1]],facecolor=INK))
ax.add_patch(Circle((5.4,4.85),.12,color=BLUE))
arrow(ax,(5.25,4.65),(5.25,2),BLUE);arrow(ax,(5.65,2),(5.65,4.65),ORANGE)
ax.text(3.9,3.4,'Laser pulse\nsent down',ha='right',color=BLUE)
ax.text(6.5,2.8,'Reflected light\nreturns',color=ORANGE)
ax.text(.6,5.25,'GNSS + IMU\nSensor position\nand orientation',va='top')
arrow(ax,(3.2,4.9),(4.25,4.9),INK)
ax.text(8.15,5.15,'Round-trip time: Δt\n\nDistance = c × Δt / 2\n\nc = speed of light',va='top',fontsize=13)
ax.text(.6,1.6,'A short travel time\nmeans a nearby surface.',va='top')
ax.text(5.4,.15,'Distance + sensor position/orientation → X, Y, Z coordinates',ha='center',fontsize=13)
save(fig,'lidar-pulse-distance')

# 2: Discrete returns are possible, not guaranteed.
fig, axes = plt.subplots(1,2,figsize=(11,5.5),gridspec_kw={'width_ratios':[1.15,1]})
ax=axes[0];ax.set(xlim=(0,6),ylim=(0,6));ax.axis('off');ax.set_title('2  One pulse can produce several returns',loc='left',pad=20)
ax.plot([.2,5.7],[.5,.5],color=GREEN,lw=3)
ax.add_patch(Rectangle((2.65,.5),.28,2.6,color='#947257'))
for x,y,r in [(2,3.5,1),(3.1,3.6,1.1),(2.6,4.15,.95)]:ax.add_patch(Circle((x,y),r,color='#cce5d9',alpha=.85))
ax.plot([2.8,2.8],[5.8,.55],color=BLUE,lw=2,ls='--')
for y,label,col in [(4.8,'First: canopy',GREEN),(3.05,'Intermediate: branches',ORANGE),(.55,'Last: ground',BLUE)]:
 ax.scatter([2.8],[y],s=70,color=col,zorder=5);ax.annotate(label,xy=(2.8,y),xytext=(3.25,y+.05),fontsize=11,va='bottom')
ax.text(.2,5.55,'Incoming pulse',color=BLUE,fontsize=11)
ax.text(.2,-.1,'Some pulses have only one return.\nDense cover may hide the ground.',fontsize=11)
ax=axes[1];ax.set_title('Each return becomes a point',loc='left',pad=20)
rng=np.random.default_rng(7)
x=rng.uniform(0,10,240);z=.04*x+rng.normal(0,.04,240)
ax.scatter(x,z,s=8,color=BLUE,label='Ground')
x=rng.uniform(2,5.5,240);z=2.5+1.8*np.sqrt(np.maximum(0,1-((x-3.75)/1.8)**2))+rng.normal(0,.22,240)
ax.scatter(x,z,s=8,color=GREEN,label='Vegetation')
x=rng.uniform(7,9.5,110);ax.scatter(x,3.2+rng.normal(0,.04,110),s=8,color=ORANGE,label='Roof')
ax.set(xlabel='Horizontal position',ylabel='Elevation',ylim=(-.3,5.4));ax.legend(loc='upper right',frameon=False,fontsize=10)
fig.tight_layout();save(fig,'lidar-returns-point-cloud')

# 3: DSM vs DTM, a schematic cross-section.
fig, ax=plt.subplots(figsize=(11,5.5));x=np.linspace(0,10,800);ground=.12*x+.6
surface=ground.copy();surface[(x>=2)&(x<=4)]=4.1
canopy=(x>=6)&(x<=8);surface[canopy]+=2.6*np.sqrt(np.maximum(0,1-((x[canopy]-7)/1)**2))
ax.fill_between(x,0,ground,color='#ece2d3');ax.fill_between(x,ground,surface,color='#dde9ec')
ax.plot(x,surface,color=ORANGE,lw=2.7,label='DSM: roofs, canopy, ground')
ax.plot(x,ground,color=BLUE,lw=2.7,ls='--',label='DTM: bare-earth terrain')
ax.annotate('',xy=(3,4.1),xytext=(3,.96),arrowprops=dict(arrowstyle='<->',color=INK,lw=2))
ax.text(3.2,2.4,'Height above terrain\n= DSM − DTM',va='center')
ax.text(2.1,4.4,'Building',fontsize=12);ax.text(6.55,4.45,'Tree',fontsize=12)
ax.set(xlim=(0,10),ylim=(0,5.4),xlabel='Horizontal position',ylabel='Elevation above a shared datum')
ax.set_title('3  Surface elevation is not the same as height above ground',loc='left',pad=20)
ax.legend(loc='upper left',frameon=False,fontsize=11)
ax.text(.5,-.24,'DSM − DTM requires aligned grids, matching units, and the same vertical datum.',transform=ax.transAxes,ha='center',fontsize=12)
fig.tight_layout();save(fig,'lidar-dsm-dtm-height')

# 4: A synthetic point cloud becomes pixels; no implied real measurements.
rng=np.random.default_rng(11);n=18000;x=rng.uniform(0,40,n);y=rng.uniform(0,40,n)
z=.02*x+.01*y+2;roof=(x>9)&(x<25)&(y>10)&(y<29);z[roof]+=12
z+=rng.normal(0,.12,n);z[rng.choice(n,28,replace=False)]+=rng.uniform(4,12,28)
raw=np.full((40,40),-np.inf);np.maximum.at(raw,(y.astype(int),x.astype(int)),z)
filtered=median_filter(raw,size=3)
fig,axes=plt.subplots(1,3,figsize=(12,4.6))
axes[0].scatter(x[::5],y[::5],c=z[::5],cmap='viridis',s=2,vmin=2,vmax=20)
axes[0].set_title('Points: X, Y, Z')
for ax,a,title in zip(axes[1:],[raw,filtered],['Maximum per cell','3 × 3 median of maximum']):
 ax.imshow(a,origin='lower',cmap='viridis',vmin=2,vmax=20,extent=[0,40,0,40],interpolation='nearest');ax.set_title(title)
for ax in axes:ax.set(xlim=(0,40),ylim=(0,40),aspect='equal',xlabel='X');ax.set_yticks([]);ax.set_xticks([])
fig.suptitle('4  Convert points to a raster; filtering reduces isolated high pixels',x=.05,ha='left',fontsize=15,fontweight='bold')
fig.text(.5,.03,'Color: low elevation = purple, high = yellow (synthetic units).\nIn the tutorial, IDW comes before the median. Small features can be reduced.',ha='center',fontsize=10.5)
fig.tight_layout(rect=[0,.08,1,.92]);save(fig,'lidar-points-to-raster')
