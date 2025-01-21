"""
本文档根据JS源码，把它转写为我熟悉的Python，并解释了失传的投点公式的原理。
——by Joat917, Jan 21 2025
"""

# 输入部分
num0=[100, 100, 30] # 限选人数
num1=[120, 210, 55] # 已选人数
hapy=[1.,1.,1.] # 快乐值
m=99 # 总点数
delta=0.5 # 加上一个很小的数字以避免0作为除数

assert all(map(lambda a,b:a<b, num0, num1)), "已选人数必须大于限选人数(否则不需要投点)"
l=len(num0) # 课程总数

# 输出部分
Per=[None]*3 # 人数比
mean=[None]*3 # 其他人的平均点数
X=[None]*3 # 你需要投入的点数
poss=[None]*3 # 选上概率

# 根据人数比算出其他人的平均点数
def getMeanPoint(per):
    # 先对人数比进行修正，把它掰平
    qer=(per-1)**0.125+1

    # 通过二次逼近得到原始的平均点数
    mean_0=-101*qer**2+392.6*qer-347.8

    # 对上述平均点数进行修正
    mean_1=0.92*mean_0+0.08*99

    return mean_1

# 根据已选、限选、你的投点和其他人的投点，算出选上的概率。它随x增加而从0趋于1。
def getExpectedPoss(n0, n1, x):
    "n0:已选;n1:限选;x:你的投点除以平均投点"
    return 1 - (1-n0/(n1+x))**(0.55*x+0.5)*(n1/(n1-n0))**(0.5-0.45*x)

# 主体计算部分
# 1.填充X列表，先暂时把所有的点都投进某一课程中，之后再调整
X[0]=m
for i in range(1, l):
    X[i]=0

# 2.算出别人在某一门课上的平均投点
for i in range(l):
    Per[i]=num1[i]/num0[i]
    mean[i]=getMeanPoint(Per[i])

# 3.最优化投点的分布，以让选上概率在快乐值的加权求和下最大
# 3.1 遍历列表两个指标的顺序
def iterIndexTraversal(l, a=0):
    # 首先，按顺序遍历全部课程
    for i in range(l):
        for j in range(1, l):
            # 返回点数可能减少的课程和点数可能增加的课程
            changed=yield (a+i)%l, (a+i+j)%l
            # 如果点数发生了转移
            if changed:
                # 试探点数增加了的课程是否需要把点数继续向后转移
                new_a=(a+i+j)%l
                # 重新开始遍历，直到点数不再发生转移
                yield from iterIndexTraversal(l=l, a=new_a)
                return

# 3.2 循环内部函数
def loopInnerFunction(ind1, ind2):
    # 算出转移前和转移后的概率期望差异
    old_expectation=\
        hapy[ind1]*getExpectedPoss(num0[ind1], num1[ind1], (X[ind1]+delta)/(mean[ind1]+delta)) + \
        hapy[ind2]*getExpectedPoss(num0[ind2], num1[ind2], (X[ind2]+delta)/(mean[ind2]+delta))
    new_expectation=\
        hapy[ind1]*getExpectedPoss(num0[ind1], num1[ind1], (X[ind1]-1+delta)/(mean[ind1]+delta)) + \
        hapy[ind2]*getExpectedPoss(num0[ind2], num1[ind2], (X[ind2]+1+delta)/(mean[ind2]+delta))
    
    # 如果概率期望增加，那么转移
    if old_expectation<new_expectation:
        X[ind1]-=1
        X[ind2]+=1
        return True
    return False

# 3.3 循环主体
index_yielder=iterIndexTraversal(l, a=0)
changed=None
try:
    while True:
        ind1, ind2=index_yielder.send(changed)
        changed=loopInnerFunction(ind1, ind2)
except StopIteration:
    pass

# 4. 计算选上概率
for i in range(l):
    poss[i]=getExpectedPoss(num0[i], num1[i], (X[i]+delta)/(mean[i]+delta))

# 5. 输出
print(X)
print(poss)
