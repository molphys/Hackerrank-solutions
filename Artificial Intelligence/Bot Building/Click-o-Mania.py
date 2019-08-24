#!/usr/bin/python
#solution with exhaustive DFS
#target scores 10 (10 steps), 15 (30 steps), 25 (53 steps), and 30 (67)
#(f[0],f[1]) :5,:3,:1,:0 - 0/3/50 = 3/-6
from collections import defaultdict
import sys,time

def remove_figure(x,y,z,figure_to_remove,grid,p1=0,p3=0):
    new_grid=[[*grid[i]] for i in range(x)]

    color,point_list=figure_to_remove
    for point in point_list:
        new_grid[point[0]][point[1]]='-'
    return new_grid

def collapse_grid(x,y,z,grid,p1=0,p3=0):
    #drop points down
    new_grid=[['-' for j in range(y)] for i in range(x)]
    col=0
    for j in range(y):
        row=x-1
        cnt=0
        for i in range(x-1,-1,-1):
            if grid[i][j]=='-':
                continue
            new_grid[row][col]=grid[i][j]
            row-=1
            cnt+=1
        if cnt==0: continue
        col+=1
    return new_grid

def print_two_grids(grid,new_grid,p1=0,p3=0):
    output_grid=list(zip(*grid))+[tuple(' '*20)]+list(zip(*new_grid))
    output_grid=zip(*output_grid)
    print('\n'.join(map(lambda x:''.join(x),output_grid)))

def get_figure(x,y,z,grid,PointX,PointY,color,figure,p1=0,p3=0):
    figure.add((PointX,PointY))

    if PointX>0 and (PointX-1,PointY) not in figure and grid[PointX-1][PointY]==color:
        figure.update(get_figure(x,y,z,grid,PointX-1,PointY,color,figure,p1,p3))
    if PointX<x-1 and (PointX+1,PointY) not in figure and grid[PointX+1][PointY]==color:
        figure.update(get_figure(x,y,z,grid,PointX+1,PointY,color,figure,p1,p3))
    if PointY>0 and (PointX,PointY-1) not in figure and grid[PointX][PointY-1]==color:
        figure.update(get_figure(x,y,z,grid,PointX,PointY-1,color,figure,p1,p3))
    if PointY<y-1 and (PointX,PointY+1) not in figure and grid[PointX][PointY+1]==color:
        figure.update(get_figure(x,y,z,grid,PointX,PointY+1,color,figure,p1,p3))

    return sorted(figure)

def get_figure_list(x,y,z,grid,p1=0,p3=0):
    visited=[['_' for _ in range(y)] for _ in range(x)]
    figures=[]

    #collect all figures
    for i in range(x):
        for j in range(y):
            if visited[i][j]!='_': continue
            color=grid[i][j]
            if color=='-':
                visited[i][j]='-'
                continue
            figure=list(get_figure(x,y,z,grid,i,j,color,set(),p1,p3))
            figures.append((color,figure))
            for point in figure:
                visited[point[0]][point[1]]='-'

    if p3:
        for color,figure in figures:
            print('color,len,figure=',color,len(figure),figure)
        print('\n'.join(map(lambda x:''.join(x),visited)))

    return figures  #list of color and figures (color,[list of points])

#DFS with one step forward into future result. Sort next step result by count of count of 1 block size figures
#grid_list=[(float(inf("inf"),float("inf"),grid)] -> [(initial count of 1 block size figures, count of 2 and block size figures,grid)]
def dfs(x,y,z,grid_list,level,p1=0,p3=0):
    global out_file,out_file_name,end_time


    min_ones=float("inf")
    min_figs=float("inf")
    min_route=[(None,None)]
    min_frgs=float("inf")

    step=0
    for ones,figs,frgs,prev_figure,figures,grid in grid_list:
        #for each parsed grid and it's figures calculate ones/figs after removing. Build new grid list for deeper level
        new_grid_list=[]
        for i in range(len(figures)):
            if p3:
                if i>2: break
            figure_to_remove=figures[i]
            ##can't remove one block figure
            if len(figure_to_remove[1])==1:
                continue
            if p3: print('figure_to_remove=',figure_to_remove)
            new_grid=remove_figure(x,y,z,figure_to_remove,grid,p1,p3)
            new_grid=collapse_grid(x,y,z,new_grid,p1,p3)
            new_figures=get_figure_list(x,y,z,new_grid,p1,p3)
            new_ones,new_figs,new_frgs=0,0,0
            new_prev_figure=figure_to_remove[1]  #figure without color
            new_sqrs=defaultdict(int)
            new_sqrs1=defaultdict(int)
            for color,figure in new_figures:
                new_sqrs[color]+=len(figure)
                if len(figure)==1:
                    new_ones+=1
                    new_sqrs1[color]+=1
                else:
                    new_figs+=1
            for color in new_sqrs.keys():
                if new_sqrs1[color]==1 and new_sqrs[color]==1:
                    new_frgs=float("inf")
                    continue
                else:
                    new_frgs+=new_sqrs1[color]/new_sqrs[color]

            ##save minimal value for current level
            if (min_ones,min_frgs)>(new_ones,new_frgs):
                min_frgs=new_frgs
                min_ones=new_ones
                min_figs=new_figs
                if len(prev_figure)>0:
                    prev_point=[prev_figure[0]]
                else:
                    prev_point=[]
                min_route=prev_point+[new_prev_figure[0]]

            ##do not follow dead ends
            if new_frgs==float("inf"):
                if p3: print('Dead end. Terminate this branch=',figure_to_remove[0],figure_to_remove[1][0])
                continue

            ###### solution has been found!!!!!
            if new_ones==0 and new_figs<=2:
                if len(prev_figure)>0:
                    prev_point=[prev_figure[0]]
                else:
                    prev_point=[]
                if p1: print('Solution has been found level=',level,prev_point+[new_prev_figure[0]])
                return (0,0,0,prev_point+[new_prev_figure[0]])

            new_grid_list.append((new_ones,new_figs,new_frgs,new_prev_figure,new_figures,new_grid))

        #if new grids are found, launch DFS for the deeper level
        if new_grid_list!=[]:
            #basic sort by count of 1 block size figures, count of 2 and block size figures,
            new_grid_list.sort(key=lambda f:(f[0],f[1],1*len(f[3]),-1*f[3][0][1],1*f[3][0][0]))

            new_grid_list=new_grid_list[:5]
            #if level>=1: new_grid_list=new_grid_list[:5]
            if level>=5: new_grid_list=new_grid_list[:1]
            if level>=70: new_grid_list=[]
            next_ones,next_figs,next_frgs,next_route=min_ones,min_figs,min_frgs,min_route
            next_ones,next_figs,next_frgs,next_route=dfs(x,y,z,new_grid_list,level+1,p1,p3)

            if p1 and (level>=0 and level<=2) and next_ones>=0:  #or target_point in selected_points
                if out_file_name[:3]!='sys':
                    out_file=open(out_file_name,'a')
                else:
                    out_file=sys.stdout
                print('\nlevel',level,'-',step,' prev_figure',[prev_figure[i] for i in range(len(prev_figure)) if i<1],
                      ' new_ones=',new_ones,' new_figs=',new_figs,'figures',len(figures),file=out_file)
                print('    ones=',list(map(lambda f:f[0],new_grid_list)),file=out_file)
                print('    figs=',list(map(lambda f:f[1],new_grid_list)),file=out_file)
                print('    frgs=',list(map(lambda f:int(f[2]*1e4)/1e4,new_grid_list)),file=out_file)
                print('    lens=',list(map(lambda f:len(f[3]),new_grid_list)),file=out_file)
                print('  points=',list(map(lambda f:f[3][0],new_grid_list)),file=out_file)
                print('   result',next_ones,next_figs,next_route[:],file=out_file)
                print('    selected_points',list(map(lambda x:x[3][0],new_grid_list)),'\n')
                if out_file_name[:3]!='sys': out_file.close()

            if next_ones==0 and next_figs<=2:
                if len(prev_figure)>0:
                    prev_point=[prev_figure[0]]
                else:
                    prev_point=[]
                #if solution has been found at next deeper levels
                if p3: print('Solution has been found level=',level,prev_point+next_route)
                return (0,0,0,prev_point+next_route)
            else:
                #save minimal value
                if (min_ones,min_frgs)>(next_ones,next_frgs):
                    min_ones=next_ones
                    min_figs=next_figs
                    min_frgs=next_frgs
                    if len(prev_figure)>0:
                        prev_point=[prev_figure[0]]
                    else:
                        prev_point=[]
                    min_route=prev_point+next_route
                if time.time()>end_time:
                    return (min_ones,min_figs,min_frgs,min_route)
        step+=1

    #no solution has been found :-((
    #(count of 1 block size figures, count of 2 and block size figures,backtrack route[points])
    return (min_ones,min_figs,min_frgs,min_route)

def nextMove(x,y,z,grid,p1=0,p3=0):
    global out_file,out_file_name,end_time
    end_time=time.time()+120
    print(end_time)

    ones=float("inf")  #initial value for grid
    figs=float("inf")  #initial value for grid
    frgs=float("inf")  #initial value for grid
    prev_point=[]  #empty list of points
    figures=get_figure_list(x,y,z,grid,p1,p3)  #initial figure list
    level=0  #current level of DFS
    out_file_name='sys'
    if out_file_name[:3]!='sys':
        out_file=open(out_file_name,'w')  #save output to file
        out_file.close()
    ones,figs,frgs,route=dfs(x,y,z,[(ones,figs,frgs,prev_point,figures,grid)],level,p1,p3)

    #return result
    print('==ones==',ones,file=sys.stderr)
    print('==figs==',figs,file=sys.stderr)
    print('==frgs==',frgs,file=sys.stderr)
    print('==route==',route,file=sys.stderr)
    DIR=str(route[0][0])+' '+str(route[0][1])
    print(DIR)

if __name__=='__main__':
    p1=1
    p2=0
    p3=0
    ff=0

    #25 points
    s=iter('''20 10 5
    OBYRORBYGB
    YYRGOBRBYB
    BOYGYRYOYR
    GYYOGYOBBY
    GOBGGYOGRR
    OBBRBOYRBB
    RRGYBRBGOY
    GRYRGYGGOR
    YOBOOGOBGG
    YRBOGYBBGG
    RRGOYBYYYY
    YBBRBBRGGG
    RGBYYBBRGY
    YBYOBRBOGG
    OBYGOGROOR
    RGBOORBBBR
    GOGOBRORGG
    GGYBOBYRGB
    YBYORYGBOR
    GYROOOOBOG'''.split('\n'))
    #test
    s=iter('''20 10 6
----------
----------
----------
----------
----------
----------
----------
----------
----------
----------
----------
----------
----------
----------
----------
----------
Y---------
R---------
B---------
RBYY------'''.split('\n'))
    #30 points 17 4 (-6)
    s=iter('''20 10 6
    BGOBVBGROB
    YBYBVGRRGG
    VYOOYYYBBB
    VRRRVOBGBG
    OOOVYBYYVR
    VGBYYOYYGB
    OOYOYVGOBV
    ROROYOYYOY
    BRRYYROVYB
    RRYRBGGRRV
    OGYGVOVYOR
    GYBYYBOVGV
    GOOBOVOVOB
    OGVORVGVVY
    GOYVOVRRGV
    GORVYBYOBV
    VGYYBYBGYG
    RGVYOOVBOG
    GVVGVVRBYB
    VBOBYYOORO'''.split('\n'))


    if ff==0:
        x,y,k=[int(i) for i in next(s).strip().split()]
        grid=[[i for i in str(next(s).strip())] for _ in range(x)]
        nextMove(x,y,k,grid,p1,p3)
    else:
        x,y,k=[int(i) for i in input().strip().split()]
        grid=[[i for i in str(input().strip())] for _ in range(x)]
        nextMove(x,y,k,grid)

    #erase data in file during debugging on personal laptop
    try:
        fptr=open('1.txt','w')
        fptr.close()
    except:
        pass
