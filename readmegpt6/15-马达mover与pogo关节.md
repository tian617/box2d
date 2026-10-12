# 15 · 马达、mover 与 pogo 关节

[返回目录](./README.md) · [上一章](./14-旋转棱柱轮与焊接关节.md)

> 基线：Box2D 3.2.0，提交 `dc67c40ba2ce1ad384b0c985dbc1b539cba9221b` 的当前工作树。
> 本章回答“如何驱动物体，但仍允许力不够、仍接受碰撞与反作用”。
> 也会分清名字相近的 mover 关节与角色碰撞查询，不把二者误讲成同一求解器。

## 1. 先分清四种目的

| 对象 | 主要目标 | 是否主动生成约束冲量 |
|---|---|---|
| motor joint | 用有限力/力矩追踪关节位姿及相对速度 | 是 |
| mover joint | 用每个世界轴独立的力上限追踪质心相对线速度 | 是 |
| pogo joint | 用弹簧内部状态生成恢复速度，再沿指定法线施力 | 是 |
| filter joint | 管理一对刚体是否互相碰撞 | 否 |

“驱动”不等于每帧直接写位置。
直接改位置没有自动计算推动所需的冲量，也不会自然给另一物体反作用。
这些关节则仍使用刚体质量、角惯量和成对冲量更新。

所有力上限都应先乘子步时长 \(h\) 再参与冲量限幅。
线冲量单位为牛顿·秒。
角冲量单位为牛顿·米·秒。
本章沿用 \(\mu=1/m\)、\(\iota=1/I\)，以免把源码局部变量 `mA` 误看成真实质量。

## 2. Motor：位姿控制与速度控制是四个独立通道

### 2.1 当前 API 不是旧版 motor joint 参数表

[`b2MotorJointDef`](../include/box2d/types.h) 的主要字段是：

- `linearVelocity`：目标相对线速度向量。
- `maxVelocityForce`：线速度通道最大力。
- `angularVelocity`：目标相对角速度。
- `maxVelocityTorque`：角速度通道最大力矩。
- `linearHertz/linearDampingRatio/maxSpringForce`：平动位姿弹簧。
- `angularHertz/angularDampingRatio/maxSpringTorque`：角度位姿弹簧。

因此应想成四个可单独启用的执行器：

1. 平动弹簧。
2. 角度弹簧。
3. 线速度马达。
4. 角速度马达。

没有足够力时，目标只是希望达到的状态，不是硬性覆盖。
`linearVelocity` 与 `angularVelocity` 是目标速度，不是“最高允许速度”阈值。
当前这些字段并没有定义一个通用的绝对刚体速度裁剪器。

默认构造 `b2DefaultMotorJointDef` 将这些驱动量置零。
只指定两个刚体而不设置相应最大力/力矩，不会自动得到很强的跟随器。

### 2.2 目标位姿藏在两个局部关节框架里

设刚体变换为 \(X_A,X_B\)，局部关节框架为 \(F_A,F_B\)。
对应的世界关节框架为

\[
G_A=X_AF_A,\qquad G_B=X_BF_B.
\]

位置控制的目标是让两个框架重合：

\[
G_B=G_A.
\]

等价地，目标 B 变换为

\[
X_{B,target}=X_AF_AF_B^{-1}.
\]

这只是表达目标关系，不表示源码直接把该矩阵赋给 B。
实际求解仍根据当前误差产生有限冲量。

框架的平移误差为两锚点差

\[
C_p=p_B-p_A=c_B+r_B-c_A-r_A.
\]

角误差为

\[
C_\theta=\operatorname{angle}(Q_A^{-1}Q_B).
\]

\(C_p\) 单位为米，\(C_\theta\) 为弧度。
若希望 B 相对 A 保持偏移，就应设置适当的局部框架，而不是误以为目标永远是两质心重合。

### 2.3 朴素实现：先只追一个速度

最小练习可以让 A 为静态、B 的锚点位于质心。
此时暂时没有转动耦合。
按以下步骤处理：

1. 求速度误差 \(e_v=v_B-v_A-v_t\)。
2. 求标量有效质量 \(M_v=1/(\mu_A+\mu_B)\)。
3. 求理想冲量 \(\Delta P=-M_ve_v\)。
4. 将新累计冲量投影到允许的最大冲量圆盘。
5. 只施加新旧累计量之差。
6. 将相反冲量施加给 A。

这个最小版先验证“目标速度”“最大力”“质量大小”的关系。
然后才把锚点离开质心，加入下面的二维质量矩阵。

## 3. Motor 线速度通道：不是只有质心速度

### 3.1 几何速度与 Jacobian

一般锚点速度为

\[
v_{pA}=v_A+\omega_A\times r_A,
\qquad v_{pB}=v_B+\omega_B\times r_B.
\]

线速度通道误差为

\[
e_v=v_{pB}-v_{pA}-v_t.
\]

\(v_t\) 是 `linearVelocity`，单位为米每秒。
本版直接从世界空间锚点相对速度减去该向量，没有在 Solve 中再按 A 框架旋转它。
若应用希望“角色面向方向的前进速度”，应先转换为所需世界向量。

Jacobian 与点对点关节相同：

\[
J_p=
\begin{bmatrix}
-1&0&r_{Ay}&1&0&-r_{By}\\
0&-1&-r_{Ax}&0&1&r_{Bx}
\end{bmatrix}.
\]

### 3.2 完整线有效质量

令

\[
K_p=
\begin{bmatrix}
\mu_A+\mu_B+\iota_Ar_{Ay}^2+\iota_Br_{By}^2
&-\iota_Ar_{Ax}r_{Ay}-\iota_Br_{Bx}r_{By}\\
-\iota_Ar_{Ax}r_{Ay}-\iota_Br_{Bx}r_{By}
&\mu_A+\mu_B+\iota_Ar_{Ax}^2+\iota_Br_{Bx}^2
\end{bmatrix}.
\]

\(K_p\) 单位为每千克，\(M_p=K_p^{-1}\) 单位为千克。
理想线速度冲量为

\[
\Delta P_{trial}=-M_pe_v.
\]

如果两个锚点偏心，线速度驱动可以产生角速度。
所以 motor 的线驱动和角驱动可能通过力臂彼此影响。
不能把它永远当成两个互不相关的质心力。

### 3.3 圆盘限幅，而不是逐轴限幅

设 \(P_{trial}=P_{old}+\Delta P_{trial}\)。
允许的累计线冲量满足

\[
\|P\|\le hF_{max}.
\]

投影公式为

\[
P_{new}=
\begin{cases}
P_{trial},&\|P_{trial}\|\le hF_{max},\\
\dfrac{hF_{max}}{\|P_{trial}\|}P_{trial},&\text{否则}.
\end{cases}
\]

实际施加 \(\Delta P=P_{new}-P_{old}\)。
投影保留方向，只限制合力大小。
若分别把 x、y 都限制到 \(hF_{max}\)，对角线最大合力会变成原来的 \(\sqrt2\) 倍，这不是当前 motor 语义。

### 3.4 完整数值例：目标 3–4，冲量 6–8，再整体限幅

A 静态，B 质量 \(2\) 千克，锚点在质心。
所以 \(\mu_B=0.5\)，\(M_p=2I_2\)。
初始线速度零，目标 \(v_t=(3,4)\) 米每秒。
取 \(h=0.1\) 秒、最大速度驱动力 \(10\) 牛顿，旧冲量零。

\[
e_v=(-3,-4),\qquad\Delta P_{trial}=(6,8)\ \mathrm{N\,s}.
\]

其长度为 \(10\) 牛顿·秒，但上限只有 \(hF=1\)。
所以

\[
P_{new}=\frac1{10}(6,8)=(0.6,0.8).
\]

B 的速度成为

\[
v_B'=0+0.5(0.6,0.8)=(0.3,0.4)\ \mathrm{m/s}.
\]

检查平均力：\(P/h=(6,8)\) 牛顿，合力大小为 \(10\) 牛顿。
目标速度的方向被保留，但受限于这一子步只能提供的冲量。

## 4. Motor 角速度与位姿弹簧

### 4.1 角速度通道

角速度误差为

\[
e_\omega=\omega_B-\omega_A-\omega_t.
\]

Jacobian 为 \([0,0,-1,0,0,1]\)。
有效惯量

\[
M_\theta=1/(\iota_A+\iota_B).
\]

试算增量与累计限幅为

\[
\Delta\lambda_{trial}=-M_\theta e_\omega,
\]

\[
\lambda_{new}=\operatorname{clamp}
(\lambda_{old}+\Delta\lambda_{trial},-h\tau_{max},h\tau_{max}).
\]

在前例中再取 B 惯量 \(4\) 千克·平方米，角目标 \(2\) 弧度每秒。
\(M_\theta=4\)，理想冲量 \(8\)。
若最大力矩 \(5\) 牛顿·米，\(h=0.1\)，只能施加 \(0.5\) 牛顿·米·秒。
角速度增加 \(0.25\times0.5=0.125\) 弧度每秒。

### 4.2 平动弹簧

第 13 章推导的软约束形式现在变成向量：

\[
\Delta P_s=-S_p M_p(\dot C_p+B_pC_p)-T_pP_{s,old}.
\]

\(\dot C_p=v_{pB}-v_{pA}\)，这里不减线速度通道目标。
位置弹簧和速度马达分别表达各自的需求。

平动弹簧的累计量独立限制到

\[
\|P_s\|\le h\,\texttt{maxSpringForce}.
\]

只有 `maxSpringForce>0` 且 `linearHertz>0` 才执行该通道。
频率零在这里表示不执行位置弹簧，不是 weld 那样的刚性替代模式。

### 4.3 角度弹簧

角度弹簧为

\[
\Delta\lambda_s=-S_\theta M_\theta
(\omega_B-\omega_A+B_\theta C_\theta)-T_\theta\lambda_{s,old}.
\]

独立限制到 \(\pm h\,\texttt{maxSpringTorque}\)。
只有 `maxSpringTorque>0` 且 `angularHertz>0` 才执行。
正角误差对应负恢复角冲量，促使 B 相对 A 向回转。

### 4.4 位姿弹簧完整限幅例

本例独立于前面的速度驱动例，初始速度重新取零。
A 静态，B 质量 \(2\)、惯量 \(4\)，锚点在质心。
取 \(h=0.1\)、\(\Omega=10\)、\(\zeta=0.5\)。
所以 \(B=5,S=2/3,T=1/3\)。

位置误差 \(C_p=(0.2,-0.1)\) 米，旧弹簧冲量零：

\[
\Delta P_{trial}=-\frac23\times2\times5(0.2,-0.1)
=(-4/3,2/3).
\]

长度为 \(\sqrt{20}/3\approx1.490712\) 牛顿·秒。
若最大弹簧力为 \(5\) 牛顿，则冲量圆盘半径为 \(0.5\)。
因此

\[
P_s=(-1/\sqrt5,1/(2\sqrt5))
\approx(-0.447214,0.223607).
\]

线速度变化为

\[
\Delta v_B=0.5P_s\approx(-0.223607,0.111803)\ \mathrm{m/s}.
\]

角误差再取 \(0.2\) 弧度，角弹簧理想冲量为

\[
\Delta\lambda_{trial}=-\frac23\times4\times(5\times0.2)=-8/3.
\]

若最大弹簧力矩为 \(2\) 牛顿·米，冲量下限是 \(-0.2\)。
实际角速度变化为 \(0.25\times(-0.2)=-0.05\) 弧度每秒。
两个通道都朝恢复位姿方向作用，又都没有超出自己的能力上限。

### 4.5 四通道的上限不是一个共享预算

本版分别保存线速度冲量、角速度冲量、线弹簧冲量、角弹簧冲量。
例如线速度力上限为 \(10\) 牛顿、线弹簧力上限为 \(5\) 牛顿。
不能据此断言总 motor 线力仍永远不超过 \(10\) 牛顿。
两通道同向饱和时，总量可以接近 \(15\) 牛顿。
反向时则可能互相抵消。

若业务需要一个严格共享的总力预算，需要在设计层面另行处理，不能假装当前两个独立限幅已经实现该需求。

## 5. Motor 的实际求解顺序与优化

`b2PrepareMotorJoint`，`motor_joint.c:179-249`，准备两框架、质量矩阵及两组软度。
`b2WarmStartMotorJoint`，`251-285`，先把两组线冲量相加、两组角冲量相加，再施加到速度。
`b2SolveMotorJoint`，`287-436`，顺序为：

1. 角弹簧。
2. 角速度马达。
3. 平动弹簧。
4. 线速度马达。

角度通道的结果会影响后面的锚点速度。
因此不能让四通道都读取同一份旧速度，最后才统一应用。

Prepare 计算初始 `linearMass`。
正频率线弹簧执行时，Solve 根据当前力臂再次更新这个逆矩阵。
后面的线速度通道使用当前存储的 `linearMass`。
若线弹簧关闭，线速度通道使用先前 Prepare 的矩阵。
这是源码的具体缓存策略，不应概括为“所有分支每次都重算矩阵”。

`b2SolveMotorJoint` 不接收 `useBias`。
统一分发调用它时，不会因为 relax 而自动关闭这些驱动通道。

## 6. Mover joint：两个世界轴上的有限力速度追踪

### 6.1 先纠正同名概念

[`src/mover_joint.c`](../src/mover_joint.c) 不收集碰撞平面。
它不扫描胶囊，不沿墙滑动，也不在这个函数里处理台阶。
它的物理目标很明确：

\[
v_B-v_A=v_t.
\]

这里是质心线速度，不是偏心锚点速度。
没有 \(\omega\times r\) 项。

Prepare 显式将这条关节缓存中的 `invIA/invIB` 设为零。
这不修改刚体真实惯量，只表示此关节不通过角自由度求响应。

### 6.2 Jacobian 和标量有效质量

二维 Jacobian 为

\[
J_m=
\begin{bmatrix}
-1&0&0&1&0&0\\
0&-1&0&0&1&0
\end{bmatrix}.
\]

因此

\[
K_m=(\mu_A+\mu_B)I_2,
\qquad M_m=\frac1{\mu_A+\mu_B}.
\]

\(M_m\) 单位为千克。
同一个标量可同时用于 x、y，不需要偏心矩阵求逆。

误差与试算冲量为

\[
e=v_B-v_A-v_t,
\qquad\Delta P_{trial}=-M_me.
\]

冲量更新

\[
v_A'=v_A-\mu_A\Delta P,
\qquad v_B'=v_B+\mu_B\Delta P.
\]

角速度完全不在这段更新中。
若希望避免角色因驱动力自转，这是很有用的控制方式。
但碰撞或其他关节仍可能改变它的角速度。

### 6.3 真正的区别：累计冲量可行域是矩形

Mover 的 `maxVelocityForce` 是二维向量，不是 motor 的标量。
分别记 x、y 最大力为 \(F_x,F_y\)。
约束为

\[
-hF_x\le P_x\le hF_x,
\qquad
-hF_y\le P_y\le hF_y.
\]

所以必须逐分量投影：

\[
P_{new,x}=\operatorname{clamp}(P_{old,x}+\Delta P_x,-hF_x,hF_x),
\]

\[
P_{new,y}=\operatorname{clamp}(P_{old,y}+\Delta P_y,-hF_y,hF_y).
\]

这是一块轴对齐矩形，不是圆盘。
方向可以因为 x、y 不同程度饱和而改变。
当 \(F_y=0\) 时，这个关节不能提供竖直驱动力，即使目标竖直速度不为零。

```137:154:src/mover_joint.c
	// linear velocity
	if ( joint->maxVelocityForce.x > 0.0f || joint->maxVelocityForce.y > 0.0f )
	{
		b2Vec2 cdot = b2Sub( vB, vA );
		cdot = b2Sub( cdot, joint->linearVelocity );
		b2Vec2 b = b2MulSV( joint->linearMass, cdot );
		b2Vec2 impulse = { -b.x, -b.y };

		b2Vec2 oldImpulse = joint->linearVelocityImpulse;
		joint->linearVelocityImpulse = b2Add( joint->linearVelocityImpulse, impulse );
		b2Vec2 maxImpulse = b2MulSV( context->h, joint->maxVelocityForce );

		// clamp x and y separately
		joint->linearVelocityImpulse = b2Clamp( joint->linearVelocityImpulse, b2Neg( maxImpulse ), maxImpulse );

		impulse = b2Sub( joint->linearVelocityImpulse, oldImpulse );
		vA = b2MulSub( vA, mA, impulse );
		vB = b2MulAdd( vB, mB, impulse );
```

### 6.4 两边都动态的完整数值例

取 A 质量 \(2\)、B 质量 \(1\) 千克。
两边初始线速度零，目标相对速度为 \((3,4)\) 米每秒。

\[
\mu_A=0.5,\quad\mu_B=1,\quad M_m=2/3.
\]

取 \(h=0.1\) 秒，\((F_x,F_y)=(6,2)\) 牛顿。
理想冲量

\[
\Delta P_{trial}=\frac23(3,4)=(2,8/3).
\]

允许矩形为 \([-0.6,0.6]\times[-0.2,0.2]\)。
因此实际累计冲量为 \((0.6,0.2)\) 牛顿·秒。
旧冲量零，所以全部作为本次增量施加。

\[
v_A'=(-0.3,-0.1),\qquad v_B'=(0.6,0.2).
\]

相对速度为

\[
v_B'-v_A'=(0.9,0.3)\ \mathrm{m/s}.
\]

它没有保持目标向量 \((3,4)\) 的方向，因为 y 轴的力预算更小。
两边线动量核查：\(2(-0.3,-0.1)+(0.6,0.2)=(0,0)\)。
两边角速度不变。

平均合力大小为 \(\sqrt{6^2+2^2}\approx6.3249\) 牛顿。
它可以大于 x 分量上限 \(6\)，因为限制的是分量，不是合力模长。

### 6.5 朴素实现与本版优化

Mover 是很适合第一个实现的“有力上限速度执行器”。
只需两刚体索引、一个标量质量、一组二维累计冲量。
不必计算锚点方向、角度或二维矩阵。

本版仍使用统一的 Prepare/WarmStart/Solve 调度。
两个力上限都不为正时，Solve 清除累计冲量。
同 motor 一样，它的 Solve 不接收 `useBias`。
不要因为它可用于角色，就把它写成世界碰撞查询的一部分。

## 7. Pogo：恢复长度的方向，与施力方向可以不同

### 7.1 本版比“沿一根轴的普通弹簧”多一步

Pogo 常用来表达角色与支撑表面之间的弹性恢复。
但这份源码不是直接复制距离弹簧的软约束增量公式。
它先推进一个内部弹簧速度，再把这个速度当成法向速度目标。

必须区分两个方向：

- \(a\)：测量腿长的 pogo 轴。
- \(n\)：施加冲量的法线 `normal`。

在 `b2SolvePogoJoint` 中

\[
a=\texttt{frameB.q}\,(0,1).
\]

而 \(n\) 在创建时直接从 `def.normal` 保存。
它不是由两锚点连线归一化得到，也不是从 A 的局部 x 轴自动推导。
创建代码没有在这里代替调用者重新归一化。
使用者应提供方向正确的单位法线，才能满足下面有效质量简式的单位轴假设。

### 7.2 长度不是欧氏距离

Pogo 测量

\[
\ell=a\cdot d,
\qquad C_\ell=\ell-\ell_0.
\]

\(\ell_0\) 是 `restLength`，单位为米。
\(C_\ell<0\) 表示短于静止长度，通常需要恢复向上运动。
这不等于 \(\|d\|-\ell_0\)。

Solve 中的测长轴使用 Prepare 保存的 `frameB.q`，没有额外乘子步的 `deltaRotation`。
锚点力臂则仍按子步旋转更新。
所以要把它理解为本版具体采用的步内近似，而不是泛化成“所有方向每次都重算”。
公开的 `b2PogoJoint_GetLength` 从当前刚体变换和局部框架计算投影长度。
阅读 getter 与求解缓存时，应分别看清使用的是哪个阶段的变换。

### 7.3 从连续弹簧到内部恢复速度

设内部弹簧速度为 \(u\)，单位为米每秒。
以有效质量归一化后，弹簧阻尼方程为

\[
\dot C_\ell=u,
\qquad \dot u=-\Omega^2C_\ell-2\zeta\Omega u.
\]

\(\Omega=2\pi f\)，单位为每秒。
\(\zeta\) 是无量纲阻尼比。

使用隐式一步：

\[
u_{new}=u_{old}-h\Omega^2(C_\ell+hu_{new})-2h\zeta\Omega u_{new}.
\]

整理得到

\[
u_{new}=
\frac{u_{old}-h\Omega^2 C_\ell}
{1+2h\zeta\Omega+h^2\Omega^2}.
\]

这就是 [`b2SpringDamper`](../include/box2d/math_functions.h) 的返回式。
分母无量纲，分子是米每秒。
压缩误差为负时，\(-h\Omega^2C_\ell\) 为正，推动内部速度朝伸长方向发展。

实际 pogo 每次从当前几何重新测量 \(C_\ell\)，内部 \(u\) 则作为状态保留。
它不是独立于刚体运动、完全自行积分一根抽象弹簧长度。

### 7.4 第二阶段：沿法线追踪这个恢复速度

法线上的锚点相对速度为

\[
v_n=n\cdot(v_B+\omega_B\times r_B-v_A-\omega_A\times r_A).
\]

本阶段目标为

\[
v_n=u_{new}.
\]

固定当前法线时，Jacobian 为

\[
J_n=[-n_x,-n_y,-r_A\times n,\ n_x,n_y,r_B\times n].
\]

逆有效质量

\[
K_n=\mu_A+\mu_B+\iota_A(r_A\times n)^2+\iota_B(r_B\times n)^2,
\qquad M_n=1/K_n.
\]

上式说明有效质量的来源。本版在 Prepare 用初始力臂计算并缓存 `linearMass`（`pogo_joint.c` 第 145–152 行）；Solve 更新当前力臂，但仍使用这份缓存质量，并不重新求它的倒数。

源码将偏置设为 \(b=-u_{new}\)，因此

\[
\Delta\lambda_{trial}=-M_n(v_n+b)=-M_n(v_n-u_{new}).
\]

最后按拉力与压力两个上限投影累计量：

\[
-hF_{tension}\le\lambda\le hF_{compression}.
\]

两上限参数本身是非负的力大小。
负冲量是沿 \(-n\) 拉，正冲量是沿 \(+n\) 推。
这与 distance 的 `lowerSpringForce` 直接保存有符号下界的 API 形式不同。

实际线冲量 \(P=\Delta\lambda n\)。
两刚体仍接受等大反向线冲量及相应偏心角冲量。

### 7.5 为什么不能把整个 pogo 写成一个长度 Jacobian

测量误差用 \(a\)，最终施力速度用 \(n\)。
当 \(a\ne n\) 时，这不是对同一个 \(a\cdot d\) 约束直接使用其完整梯度求解。
它是“弹簧恢复目标生成器 + 法向速度执行器”的组合。

源码注释提到：若要补偿方向夹角，可以考虑除以 \(n\cdot a\)。
但当法线近乎垂直于测长轴时，分母很小，恢复速度会被放大得很大。
当前实现宁可恢复慢一些，也不做这种危险放大。

这属于明确的控制与稳定性选择，不应包装成一个没有近似的各向同性弹簧。

## 8. Pogo 有偏置求解阶段的数值代入

以下三个例子各自独立，均重置旧内部弹簧速度和旧累计冲量为零，只考察一次 `useBias=true` 求解，不把其速度误当成包含 Relax 后的子步末速度。第 9 节再补完整阶段对照。

### 8.1 平地压缩，恢复力不够时只能先刹住下落

A 静态地面，B 质量 \(2\) 千克。
锚点在质心，\(n=a=(0,1)\)。
当前投影长度 \(0.8\) 米，静止长度 \(1\) 米。
所以 \(C_\ell=-0.2\) 米。

取 \(h=0.1\) 秒、\(\Omega=10\)、\(\zeta=0.5\)、旧内部速度零。

\[
u_{new}=\frac{0-0.1\times100\times(-0.2)}
{1+2\times0.1\times0.5\times10+0.1^2\times100}
=\frac23\ \mathrm{m/s}.
\]

B 当前竖直速度为 \(-1\) 米每秒。
因此 \(v_n=-1\)，\(M_n=2\)。

\[
\Delta\lambda_{trial}=-2(-1-2/3)=10/3\ \mathrm{N\,s}.
\]

若最大压缩推力为 \(20\) 牛顿，一子步最多提供 \(2\) 牛顿·秒。
旧冲量零，所以实际 \(\lambda=2\)。

\[
v_{By}'=-1+0.5\times2=0.
\]

本轮只刹住下落，尚未达到内部希望的 \(2/3\) 米每秒上升速度。
这是力预算不足，不是把恢复速度的正负号写反。
若推力预算至少允许 \(10/3\) 冲量，才可在这一独立阶段达到目标。

### 8.2 斜面：同样恢复目标，竖直恢复会变慢

重新取初始 B 速度零，其余参数相同。
令测长轴仍为 \(a=(0,1)\)，法线改为 \(n=(0.6,0.8)\)。
它已经是单位向量，\(n\cdot a=0.8\)。
内部恢复速度仍为 \(u=2/3\)。

\[
\lambda=2\times\frac23=\frac43\ \mathrm{N\,s}.
\]

在足够的力预算下，B 速度变化为

\[
\Delta v_B=0.5\times\frac43(0.6,0.8)=(0.4,8/15).
\]

检查法线目标：

\[
n\cdot\Delta v_B=0.6\times0.4+0.8\times\frac8{15}=\frac23.
\]

但竖直速度只有 \(8/15\approx0.533333\) 米每秒。
它等于 \(0.8u\)，不是 \(u\)。
这正好展示未除以 \(n\cdot a\) 的实际效果。

### 8.3 拉力上限控制贴地强度

改成平地 \(n=a=(0,1)\)，长度误差 \(+0.2\) 米、当前刚体速度零。
内部目标变成 \(-2/3\) 米每秒。
理想冲量为 \(-4/3\) 牛顿·秒。

若最大拉力为 \(3\) 牛顿，\(h=0.1\)，下界为 \(-0.3\)。
实际竖直速度变化为 \(0.5(-0.3)=-0.15\) 米每秒。
若最大拉力为零，下界就是零，Pogo 不会主动把 B 向下拉。

因此拉力不是压力参数的另一个名字。
它决定“允许多强地贴向支撑表面”。

## 9. Pogo 的真实分支与状态保存

`b2SolvePogoJoint` 只有在 `useBias=true` 时更新内部弹簧速度，并令 \(b=-u\)。
当 `useBias=false` 时，本轮 \(b=0\)，不再次推进内部弹簧速度。
它仍执行法线速度冲量步骤，并应用相同的拉压累计限幅。
不要把 relax 说成“这个关节完全不工作”。

以第 8.2 节为例，保持质心锚点、无其他外力或约束、足够力预算，补全子步的阶段表：

| 阶段 | B 速度（m/s） | 累计法线冲量（N·s） | 累计位置变化（m） |
|---|---|---:|---|
| 开始 | `(0,0)` | 0 | `(0,0)` |
| 有偏置 Solve | `(0.4,8/15)` | `4/3` | `(0,0)` |
| 以 0.1 s 积分位置 | 同上 | `4/3` | `(0.04,4/75)` |
| Relax | `(0,0)` | 0 | 保留 `(0.04,4/75)` |

最后一行来自 \(\Delta\lambda=-2\times(2/3)=-4/3\) N·s：把本轮为修位置而施加的冲量撤回，速度回到零；之前已经积分的位置不倒退。实际有重力或其他接触时，应把它们也纳入阶段状态，不能套用这一孤立例子的最终零速度。

当 `hertz==0`，WarmStart 与 Solve 都清除 `impulse` 并返回。
这里零 Hz 表示这条 Pogo 不施加弹簧冲量，不表示刚性腿。

[`b2PogoJointDef`](../include/box2d/types.h) 有初始 `impulse` 和 `velocity` 字段。
头文件说明 Pogo 常每帧重建，因此允许调用者把内部状态传递到下一条新关节。
若每帧重建时总把两者清零，响应会失去原有连续性。

`b2PogoJoint_GetImpulse` 与 `b2PogoJoint_GetVelocity` 可获取这些状态。
旧支撑完全改变时，是否继续沿用状态应由控制器评估。
不要把任意旧法线方向上的冲量无条件当成新支撑的正确初值。

这里描述的是当前实现及其约束方向。
不能因为源码注释出现“位置修正”，就声称当前函数直接执行了胶囊扫掠或完整的防穿透位置求解；实际函数更新的是内部速度与刚体速度。

## 10. Filter joint：没有冲量，但仍有逻辑用途

### 10.1 它不是零刚度弹簧

Filter 不要求两物体靠近，也不限制相对速度。
因此没有要写入求解器的 Jacobian 行，没有有效质量，也没有可施加的 \(\lambda\)。
把它当成“弹簧刚度设零”会混淆对象职责。

`b2PrepareJoint`、`b2WarmStartJoint`、`b2SolveJoint` 的 filter 分支都不调用力学求解。
`b2GetJointConstraintForce` 的 filter 分支返回零向量。
`b2GetJointConstraintTorque` 对 filter 返回零。

### 10.2 禁止碰撞来自 collideConnected

默认 `b2JointDef` 的 `collideConnected` 为 false。
Filter 默认因此能表达“这两个刚体不要相互产生普通碰撞接触”。

实际判断在 [`b2ShouldBodiesCollide`](../src/body.c)：
只要连接这两个刚体的某条关节满足 `collideConnected==false`，就返回不碰撞。
判断依据是这项设置，不是看到 `filter` 类型就无条件永久禁碰。

所以更准确的表述是：
Filter 是不施力的关节关系，通常利用默认关闭的相连体碰撞来做成对过滤。
若改成允许碰撞，它不会因为类型名而偷偷继续施加力学约束或必然禁止接触。
其他过滤条件仍可能阻止碰撞。

### 10.3 改开关为什么还要操作宽阶段

`b2Joint_SetCollideConnected`：

- 改为 false 时，销毁两刚体间已有接触。
- 改为 true 时，将一边的形状代理重新加入宽阶段移动缓冲，促使重新寻找可能接触。

这解释了为什么“只改一个布尔值”并不足以完整维护已存在的接触状态。
Filter 虽然不算力，仍参与对象关系与碰撞生命周期。

数值上，无论两体原先质量和速度如何，Filter 自身这一轮的 \(\Delta v\)、\(\Delta\omega\) 都为零。
碰撞被禁用后，原本可能产生的接触冲量也不会由 Filter 补出来。

## 11. 与角色移动查询明确分开

名字相近，但下面这些函数属于另一条工作流：

| 接口 | 输入/输出核心 | 是否直接求成对刚体关节冲量 |
|---|---|---|
| `b2World_CastMover` | 扫描胶囊位移，返回运动比例 fraction | 否 |
| `b2World_CollideMover` | 查询胶囊附近碰撞，通过回调返回平面结果 | 否 |
| `b2SolvePlanes` | 根据碰撞平面修正目标位移，返回 `delta` | 否 |
| `b2ClipVector` | 按已生效的平面裁剪向量的入射分量 | 否 |
| `b2SolveMoverJoint` | 对两刚体的线速度施加有反作用的有限冲量 | 是 |

`b2World_CastMover` 位于 `physics_world.c:2868-2924`。
它读取世界形状，进行胶囊扫描，返回可用比例。
返回一个数，不等于已经把刚体运动到那个位置。

`b2World_CollideMover` 位于 `physics_world.c:2970-3019`。
它用 AABB 与树查询寻找相关形状，并把碰撞平面交给调用者。

`b2SolvePlanes` 位于 `mover.c:7-53`。
它迭代修正几何位移，`push` 是位移修正量，不是牛顿·秒的刚体冲量。
不要因为也使用“累计并限幅”，就把两者当成同一个物理量。

`b2ClipVector` 位于 `mover.c:56-71`。
它裁掉指向已生效约束平面内部的分量。
这不是调用 `b2SolveMoverJoint` 的某个隐藏步骤。

应用可以把查询结果用于选择 Pogo 支撑或驱动目标。
但这种组合是应用层控制逻辑，不是同名函数自动互相调用的保证。

## 12. 从零搭建时的调试顺序

第一步只做 mover 的有限力相对速度控制。
检查一对动态体线动量是否守恒，角速度是否没有被该关节改变。

第二步实现 motor 的二维圆盘限幅。
用 \((3,4)\) 目标验证合力大小没有因对角方向增大。

第三步把锚点移离质心，加入角惯量与二维质量矩阵。
检查线力引起的角速度是否满足 \(\Delta\omega=\iota(r\times P)\)。

第四步加入独立角速度驱动和位姿弹簧。
确认四通道各自的力上限，不误当成共享预算。

第五步单独测试 Pogo 的内部标量弹簧。
先用平地，后用斜面，最后考虑每帧重建与状态传递。

最后再把碰撞查询、支撑选择和应用层角色逻辑连接起来。
如果一开始把几何投影、马达驱动、弹簧恢复混写在一个函数里，很难分辨是控制目标错、法线错还是碰撞结果错。

## 13. 源码索引

| 内容 | 文件与准确入口 |
|---|---|
| Motor 参数 | [`types.h`](../include/box2d/types.h)，`b2MotorJointDef:706-743` |
| Mover 参数 | `b2MoverJointDef:752-765` |
| Pogo 参数与传递状态 | `b2PogoJointDef:773-806` |
| Motor 三阶段 | [`motor_joint.c`](../src/motor_joint.c)，`179` / `251` / `287` |
| Motor 线速度圆盘限幅 | `motor_joint.c:398-422` |
| Mover 三阶段 | [`mover_joint.c`](../src/mover_joint.c)，`50` / `94` / `120` |
| Mover 逐轴限幅 | `mover_joint.c:137-158` |
| Pogo 法线直接保存 | [`joint.c`](../src/joint.c)，`b2CreatePogoJoint:521-561`，特别是 `549` |
| Pogo 三阶段 | [`pogo_joint.c`](../src/pogo_joint.c)，`98` / `160` / `200` |
| Pogo 测长与内部速度 | `pogo_joint.c:233-252` |
| Pogo 法线冲量与拉压上限 | `pogo_joint.c:254-268` |
| 隐式弹簧标量式 | [`math_functions.h`](../include/box2d/math_functions.h)，`b2SpringDamper:832-837` |
| Filter 返回零力 | `joint.c:1089-1090` |
| Filter Solve 空分支 | `joint.c:1514-1515` |
| 成对关节碰撞判断 | [`body.c`](../src/body.c)，`b2ShouldBodiesCollide:2076-2111` |
| 碰撞开关维护 | `joint.c:907-951` |
| 角色扫描与平面查询 | [`physics_world.c`](../src/physics_world.c)，`2868` / `2970` |
| 几何平面求解与裁剪 | [`mover.c`](../src/mover.c)，`7` / `56` |

## 14. 习题与答案

### 题 1：Motor 与 mover 的线冲量可行域有什么不同

答案：Motor 是半径 \(hF_{max}\) 的圆盘；mover 是半宽分别为 \(hF_x,hF_y\) 的轴对齐矩形。
前者限制合力大小，后者限制每个世界分量。

### 题 2：Mover 的竖直最大力为零，目标竖直速度不为零，会怎样

答案：该关节无法提供竖直驱动冲量。
它不会为了满足速度目标而绕过竖直力预算，也不会自动改为碰撞平面解算。

### 题 3：Motor 的线速度目标是否自动随 A 的朝向旋转

答案：本版 Solve 直接从世界锚点相对速度减 `linearVelocity`，没有在该处进行局部到世界的旋转。
需要局部前进方向时，应用应提供转换后的目标向量。

### 题 4：Pogo 的 normal 是否一定等于测长轴

答案：不一定。
测长轴来自 B 关节框架局部 y 轴，normal 是创建时提供的方向。
两者不一致时，本版不会除以它们的点积来强行补偿恢复速度。

### 题 5：Pogo 的频率零是否构成刚性悬挂

答案：不是。WarmStart 与 Solve 都清除冲量并返回。
Weld 的零频率刚性替代语义不能套在 Pogo 上。

### 题 6：Filter 是否通过“反向接触冲量”抵消碰撞

答案：不是。它不产生约束冲量。
通常通过 `collideConnected=false` 使这对刚体不产生对应普通接触，而不是先碰撞再抵消。

### 题 7：`b2SolvePlanes` 的 push 能直接当作关节反作用冲量吗

答案：不能。它是几何位移修正量，没有使用成对刚体质量和惯量。
单位、目标、状态更新路径都不同。

### 题 8：两个 motor 线通道最大力分别 10 N 与 5 N，总力上限一定 10 N 吗

答案：不是。这是独立预算；同向可相加，反向可抵消。
要共享总预算，需要另行设计，而不能从当前参数名自行推断。

[返回目录](./README.md)
