# 11 · 软约束、子步进与Relax

[返回总目录](./README.md) · [上一章](./10-累计冲量摩擦与热启动.md) · [下一章](./12-接触求解器逐行导读与完整算例.md)

> 本章从弹簧阻尼微分方程推到 `b2MakeSoft` 三系数，再解释子步与Relax为何按当前顺序执行。
> 源码基准：Box2D 3.2.0，提交 `dc67c40ba2ce1ad384b0c985dbc1b539cba9221b`。

## 1. 为什么只消除接近速度还不够

物体已经穿入地面2cm时，只令接触点法向速度为零，它可能永远停在穿透位置。

另一种极端是要求一个子步纠正全部穿透：

\[
u_{\mathrm{target}}=-\frac{s}{h}.
\]

取 \(s=-0.02\ \mathrm m\)、\(h=1/240\ \mathrm s\)，得到

\[
u_{\mathrm{target}}=4.8\ \mathrm{m/s}.
\]

对于本来应该安静支撑的接触，这可能制造明显弹跳。

因此要解决两个问题：

1. 位置误差应逐渐减小，而非永远保留。
2. 纠偏速度不应全部成为长期保留的反弹动能。

先构造可控制的弹簧阻尼响应，再讨论怎样安排求解阶段。

## 2. 一个约束方向上的弹簧阻尼模型

以下推导针对冻结几何、\(J,K,k,d\) 的单个双侧线性约束模式，假设 \(K>0,h>0,f>0,\zeta\ge0\)。齐次 ODE 暂不计外部驱动和其他约束；实际增量求解时，它们对速度的影响已反映在当前 \(u\) 中。零频率另按第 7 节的源码特殊分支处理；\(K=0\) 时不能定义 \(m_{eff}=1/K\)。

| 符号 | 含义 | 单位 |
|---|---|---|
| \(c\) | 有符号位置误差 | m |
| \(u=\dot c\) | 约束方向速度 | m/s |
| \(K=JM^{-1}J^T\) | 冲量响应系数 | kg⁻¹ |
| \(m_{eff}=1/K\) | 有效质量 | kg |
| \(k\) | 弹簧刚度 | N/m |
| \(d\) | 线性阻尼系数 | N·s/m |
| \(f\) | 自然频率 | Hz |
| \(\omega=2\pi f\) | 自然角频率 | s⁻¹ |
| \(\zeta\) | 阻尼比 | 无量纲 |
| \(h\) | 子步长度 | s |

弹簧阻尼力为

\[
F=-kc-du.
\]

结合牛顿第二定律：

\[
m_{eff}\ddot c+d\dot c+kc=0.
\]

定义

\[
k=m_{eff}\omega^2,
\qquad d=2\zeta m_{eff}\omega,
\]

便得到标准形式

\[
\boxed{\ddot c+2\zeta\omega\dot c+\omega^2c=0}.
\]

连续单自由度系统中，\(0\le\zeta<1\) 欠阻尼（其中零阻尼不衰减），\(\zeta=1\) 临界阻尼，\(\zeta>1\) 过阻尼。

接触还会单向投影、限幅并与别的刚体耦合，不能据此保证整个场景没有任何振荡。

### 2.1 为什么用频率而不是固定刚度

若不同物体采用相同 \(f,\zeta\)，则其局部 \(k,d\) 随有效质量一起变化。

这让响应的时间尺度更容易控制，而非质量变大后弹簧突然显著变慢。

例如 \(f=10\ \mathrm{Hz}\)、\(\zeta=1\)、\(m_{eff}=2\ \mathrm{kg}\)：

\[
\omega=20\pi\approx62.8319\ \mathrm{s^{-1}},
\]

\[
k=2(20\pi)^2\approx7895.6835\ \mathrm{N/m},
\quad d=4(20\pi)\approx251.3274\ \mathrm{N\,s/m}.
\]

有效质量翻倍，维持同频率需要刚度和阻尼一起翻倍。

## 3. 隐式离散：先推目标方程

记子步初误差为 \(c\)，步末速度为 \(u^+\)。

采用隐式位置近似：

\[
c^+=c+hu^+.
\]

用步末弹簧阻尼力近似本步冲量：

\[
\Lambda=hF^+=-h(kc^++du^+).
\]

代入位置：

\[
\Lambda=-hk(c+hu^+)-hdu^+
=-hkc-h(d+hk)u^+.
\]

移项并除以 \(h(d+hk)\)：

\[
\boxed{u^++\beta c+\gamma\Lambda=0},
\]

其中

\[
\beta=\frac{k}{d+hk},
\qquad \gamma=\frac1{h(d+hk)}.
\]

量纲检查：

\[
[\beta]=\mathrm{s^{-1}},\quad[\gamma]=\mathrm{kg^{-1}},
\quad[\beta c]=[\gamma\Lambda]=\mathrm{m/s}.
\]

\(\beta\) 将位置误差转成速度偏置；\(\gamma\) 将累计冲量转成柔度项。

不要把 \(\gamma\) 与无量纲阻尼比 \(\zeta\) 混淆。

## 4. 再推“当前累计基础上的增量”

当前累计猜测为 \(\Lambda\)，当前速度 \(u\) 已包含该猜测的作用。

再施加 \(\Delta\Lambda\) 后：

\[
u^+=u+K\Delta\Lambda,
\qquad \Lambda^+=\Lambda+\Delta\Lambda.
\]

代入软约束目标：

\[
u+K\Delta\Lambda+\beta c+\gamma(\Lambda+\Delta\Lambda)=0.
\]

整理：

\[
(K+\gamma)\Delta\Lambda=-(u+\beta c+\gamma\Lambda).
\]

因此

\[
\boxed{\Delta\Lambda=-\frac{u+\beta c+\gamma\Lambda}{K+\gamma}}.
\]

这才是软约束冲量修正的来源。

它不是对硬碰撞公式随意乘一个“软度百分比”。

## 5. 化成 `b2MakeSoft` 的三系数

代入 \(k=m_{eff}\omega^2\)、\(d=2\zeta m_{eff}\omega\)：

\[
\beta=\frac{\omega}{2\zeta+h\omega},
\]

\[
\gamma=\frac{K}{h\omega(2\zeta+h\omega)}.
\]

定义三个中间量：

\[
a_1=2\zeta+h\omega,
\quad a_2=h\omega a_1,
\quad a_3=\frac1{1+a_2}.
\]

于是

\[
\frac1{K+\gamma}=m_{eff}\frac{a_2}{1+a_2},
\qquad \frac{\gamma}{K+\gamma}=\frac1{1+a_2}.
\]

定义

\[
\mathrm{biasRate}=\frac{\omega}{a_1},
\quad\mathrm{massScale}=a_2a_3,
\quad\mathrm{impulseScale}=a_3.
\]

最终增量公式为

\[
\boxed{
\Delta\Lambda
=-m_{eff}\,\mathrm{massScale}(u+\mathrm{biasRate}\,c)
-\mathrm{impulseScale}\,\Lambda
}.
\]

三系数分别具有s⁻¹、无量纲、无量纲单位。

非零频率常规分支满足

\[
\mathrm{massScale}+\mathrm{impulseScale}=1.
\]

但不要把它简单说成“本帧和上帧冲量按比例混合”。

这里 \(\Lambda\) 是当前累计估计，可能已经在本子步多次更新；最后一项来自 \(\gamma\Lambda\) 柔度项。

实际计算中间量的位置：

```249:252:src/solver.h
float omega = 2.0f * B2_PI * hertz;
float a1 = 2.0f * zeta + h * omega;
float a2 = h * omega * a1;
float a3 = 1.0f / ( 1.0f + a2 );
```

返回值为：

```275:279:src/solver.h
return (b2Softness){
	.biasRate = omega / a1,
	.massScale = a2 * a3,
	.impulseScale = a3,
};
```

## 6. 一组真实参数的完整代入

取静态接触实际使用的

\[
f=60\ \mathrm{Hz},\quad\zeta=10,\quad h=1/240\ \mathrm s,
\quad m_{eff}=2/3\ \mathrm{kg}.
\]

为什么静态接触使用60Hz，将在第8节说明。

先计算

\[
\omega=120\pi\approx376.9911184308,
\]

\[
a_1=20+\frac{376.9911184308}{240}
\approx21.5707963268,
\]

\[
a_2=\frac{376.9911184308}{240}(21.5707963268)
\approx33.8833276362.
\]

于是

| 系数 | 数值 |
|---|---|
| `biasRate` | 17.4769217009612 s⁻¹ |
| `massScale` | 0.971333010129369 |
| `impulseScale` | 0.0286669898706311 |
| \(\gamma\) | 0.0442695598291461 kg⁻¹ |

取 \(c=-0.02\ \mathrm m\)、\(u=-4\ \mathrm{m/s}\)、\(\Lambda=0\)。

代码使用的速度偏置是

\[
b=\mathrm{massScale}\,\mathrm{biasRate}\,c
\approx-0.339518219271798\ \mathrm{m/s}.
\]

冲量为

\[
\Delta\Lambda=-\frac23[0.971333010129369(-4)-0.339518219271798]
\approx2.816566839859516\ \mathrm{N\,s}.
\]

新法向速度为

\[
u^+=-4+1.5(2.816566839859516)
\approx0.224850259789273\ \mathrm{m/s}.
\]

它没有变成零，因为此处求的是软约束方程。

将结果代回完整残差：

\[
u^++\beta c+\gamma\Lambda^+
\approx0.224850259789273-0.349538434019223+0.124688174229950
\approx0.
\]

这是比“系数看起来合理”更有力的验证。

注意两种偏置记号：\(b_{ODE}=\beta c\)，而未触发夹限时 \(b_{code}=\mathrm{massScale}\,b_{ODE}\)。因此源码 `velocityBias` 为 −0.3395182193 m/s，Solve 后法向速度为 +0.2248502598 m/s，并不矛盾；软式并不要求 \(u^++b_{code}=0\)。

该残差方程针对尚未投影、未夹限偏置的局部 Solve 更新，不是整个 Solve—积分—Relax 流程最终状态必须满足的方程。

接触最后仍要投影累计非负；弹簧双侧方程本身并不禁止吸引。

## 7. 零频率是特殊分支，不是连续极限

源码明确规定：

```240:247:src/solver.h
if ( hertz == 0.0f )
{
	return (b2Softness){
		.biasRate = 0.0f,
		.massScale = 0.0f,
		.impulseScale = 0.0f,
	};
}
```

因此精确零频时两个scale之和为零。

固定 \(\zeta>0\)、\(h>0\)，令数学上的 \(\omega\to0^+\)，却得到

\[
\mathrm{biasRate}\to0,
\quad\mathrm{massScale}\to0,
\quad\mathrm{impulseScale}\to1.
\]

两者不同，不能把程序分支称为普通公式的连续极限。

若 \(\zeta=0\) 且 \(\omega>0\)，则

\[
\mathrm{biasRate}=1/h,
\quad\mathrm{massScale}=\frac{(h\omega)^2}{1+(h\omega)^2},
\quad\mathrm{impulseScale}=\frac1{1+(h\omega)^2}.
\]

这也说明无阻尼时不能使用“频率趋零则biasRate必趋零”的结论。

对接触调用路径：

- \(s\le0\) 的Solve软支路采用三零系数时，本次增量为零。
- 已有缓存不会仅因为这个分支自动清空。
- Relax仍使用硬基线系数，继续解法向。
- \(s>0\) 的推测支路也仍然存在。

所以“零频让整个接触关闭”和“零频自动变无限硬”都不准确。

关节还可能有独立启用开关；特别是pogo先通过 `b2SpringDamper` 构造速度目标，不应冒充所有关节都逐字采用本章增量式。

## 8. 接触频率先夹限，再给静态接触加倍

世界步长 \(\Delta t\)、子步数 \(N\)、子步长度的关系为

\[
h=\frac{\Delta t}{N},\qquad h^{-1}=\frac{N}{\Delta t}.
\]

本版本实际有效频率为

\[
f_c=\min\left(f_{\mathrm{requested}},\frac1{8h}\right).
\]

普通接触使用 \(f_c\)，静态软度使用 \(2f_c\)。

```977:980:src/physics_world.c
// Hertz values get reduced for large time steps
float contactHertz = b2MinFloat( world->contactHertz, 0.125f * context.inv_h );
context.contactSoftness = b2MakeSoft( contactHertz, world->contactDampingRatio, context.h );
context.staticSoftness = b2MakeSoft( 2.0f * contactHertz, world->contactDampingRatio, context.h );
```

默认请求30Hz时：

| \(\Delta t\) | \(N\) | \(h\) | 普通有效频率 | 静态有效频率 |
|---|---|---|---|---|
| 1/60s | 4 | 1/240s | 30Hz | 60Hz |
| 1/60s | 1 | 1/60s | 7.5Hz | 15Hz |
| 1/30s | 2 | 1/60s | 7.5Hz | 15Hz |

因此频率设置值不能不经夹限直接代入每个算例。

普通接触满足 \(h\omega\le\pi/4\)，静态二倍频率后允许到 \(\pi/2\)。

Overflow按任一侧状态索引是否为null选择静态软度；运动学体可能逆质量为零但仍有状态，不能只检查逆质量。

## 9. 推测bias：正间隙允许有限接近速度

若当前分离 \(s>0\)，局部线性预测为

\[
s^+=s+hu.
\]

希望下一子步不越过接触边界：

\[
s+hu\ge0
\quad\Longleftrightarrow\quad
u+\frac{s}{h}\ge0.
\]

所以

\[
\boxed{b_{spec}=s/h>0}.
\]

正bias不是“向外推的速度”，而是允许仍以一定负速度接近。

例：\(s=0.03\ \mathrm m\)、\(h=0.01\ \mathrm s\)，则 \(b=3\ \mathrm{m/s}\)。

| 当前 \(u\) | 线性预测间隙 | 零缓存新接触的结果 |
|---|---|---|
| −2m/s | 0.01m | 不需要新法向冲量 |
| −5m/s | −0.02m | 需要减慢接近 |

第二行若 \(m_{eff}=1\ \mathrm{kg}\)，则

\[
\Delta\Lambda=-1(-5+3)=2\ \mathrm{N\,s},
\qquad u^+=-3\ \mathrm{m/s}.
\]

这只保证当前局部线性预测到达边界，不等于精确连续碰撞检测。

## 10. 穿透bias：软纠偏并夹住极端偏置

当 \(s\le0\) 且 `useBias=true`：

\[
b=\max(\mathrm{massScale}\,\mathrm{biasRate}\,s,-v_{\mathrm{push,max}}).
\]

其中 \(v_{\mathrm{push,max}}\) 对应 `contactSpeed`，默认SI下为3m/s。

未经夹限为−0.3395时保持原值；为−20时取−3。

必须用max：目标是避免偏置过度负向，而不是挑选更猛烈的负值。

源码增量写成

\[
\Delta\Lambda=-m_{eff}(\mathrm{massScale}\,u+b)
-\mathrm{impulseScale}\,\Lambda.
\]

注意 \(b\) 已经含 `massScale`，不能再把整个括号额外乘一次它。

夹限后不再严格等价于无限线性弹簧的隐式离散，这是额外的鲁棒性措施。

严谨说法是“夹住穿透速度偏置项”，不是承诺总接触速度、恢复速度或所有约束作用后的速度都不超过3m/s。

## 11. 子步不等于固定几何多迭代

两者在解决不同误差：

| 方法 | 每次重复改变什么 | 主要作用 |
|---|---|---|
| 固定几何多次迭代 | 冲量、速度 | 降低同一代数系统残差 |
| 子步推进 | 外力速度、冲量、位置、分离估计 | 降低时间推进及几何滞后误差 |

本版本每个子步的执行顺序是

1. 积分速度。
2. WarmStart。
3. Solve，`useBias=true`。
4. 积分位置。
5. Relax，`useBias=false`。

Prepare在循环前一次执行，Store在全部子步后执行。

`solver.c:29–30` 设置Solve和Relax各一遍；增加子步不等于在完全相同几何上重复相同方程。

`b2SolverTask` 的旧阶段注释仍列出独立Restitution，但实际执行代码没有该独立阶段，恢复已经位于Relax中。

## 12. 不重做完整窄相，怎样更新分离

保存大步开始的杆臂 \(\mathbf r_A,\mathbf r_B\)、法线 \(\mathbf n\) 和分离 \(s_0\)。

准备阶段定义

\[
s_{base}=s_0-\mathbf n\cdot(\mathbf r_B-\mathbf r_A).
\]

子步内用累计位姿增量计算

\[
s=s_{base}+\mathbf n\cdot[
\Delta\mathbf p_B-\Delta\mathbf p_A
+R(\Delta q_B)\mathbf r_B-R(\Delta q_A)\mathbf r_A].
\]

初始 \(\Delta\mathbf p=0\)、\(\Delta q=I\)，代入立刻回到 \(s=s_0\)。

这是检验是否重复加了初始杆臂的简单方法。

一个无旋转数值例：\(s_0=-0.02\)m，B相对A向上平移0.005m，则新分离为−0.015m。

实际表达式：

```275:278:src/contact_solver.c
// compute current separation
// this is subject to round-off error if the anchor is far from the body center of mass
b2Vec2 ds = b2Add( dp, b2Sub( b2RotateVector( dqB, rB ), b2RotateVector( dqA, rA ) ) );
float s = cp->baseSeparation + b2Dot( ds, normal );
```

必须区分两种用途：

- 估算分离时，使用增量旋转后的杆臂。
- 计算点速度和冲量力矩时，本版本仍使用固定杆臂。

法线和有效质量没有每子步完整重建；这是效率和稳定性的折中，不保证任意大旋转仍精确。

## 13. Relax为什么在位置积分之后

带穿透bias的Solve先产生纠偏速度，用它积分位置，穿透才会减少。

随后关闭重叠软偏置，再解法向速度，使纠偏带来的分离速度不必一直保留。

若在积分位置前就完全去掉纠偏速度，刚产生的位置修正作用也会被抵消。

教学例Solve后 \(u_n=0.18\ \mathrm{m/s}\)，\(m_{eff}=2/3\ \mathrm{kg}\)：

\[
\Delta\Lambda_{relax}=-\frac23(0.18)=-0.12\ \mathrm{N\,s}.
\]

先前累计2.7866667减少到2.6666667，但已经完成的位置推进不会回滚。

Relax也可能增加冲量。

例如30Hz普通软度算例Solve后 \(u_n\approx-0.0599786\)，则

\[
\Delta\Lambda_{relax}
=-\frac23(-0.0599786)
\approx+0.0399858\ \mathrm{N\,s}.
\]

因此它不是“永远扣掉一笔能量”的固定操作。

### 13.1 `useBias=false` 并不等于没有任何bias

| 情况 | Relax中的行为 |
|---|---|
| \(s\le0\)、无恢复目标 | 不用重叠软偏置，硬基线解法向 |
| \(s>0\) | 仍保留推测 \(s/h\) |
| 恢复目标为正 | 使用更负的恢复bias |

法向处理完成后，Relax还解滚阻和摩擦。

摩擦可以再次改变法向速度；有限遍之后可能仍有耦合残差。

Relax不直接改位置，也不以最终速度重新积分同一子步。

## 14. 朴素实现、习题与失败诊断

先实现单自由度弹簧，验证软残差；再加累计投影；最后把它放入子步时序。

**教学伪代码，非项目源码：**

```text
prepare fixed geometry and softness once
for each substep:
    integrate external-force velocities(h)
    apply cached impulses
    solve contact normals(useOverlapBias = true)
    integrate positions(h)
    solve contact normals(useOverlapBias = false)
    solve rolling resistance and friction
store impulses
```

| 习题 | 答案 |
|---|---|
| \(s=0.01,h=0.005,u=-1\)，新接触需推测冲量吗 | 不需，\(u+s/h=1\ge0\) |
| 未夹bias为−8，`contactSpeed=3` | 取−3 |
| 精确零频时两个scale之和 | 0，而非1 |
| 默认30Hz，\(\Delta t=1/30,N=2\)，普通/静态频率 | 7.5Hz、15Hz |
| 每子步是否完整重跑窄相 | 否，使用缓存几何与位姿增量估算分离 |
| Relax放位置积分前的风险 | 提前消除纠偏速度，使位置修正作用消失 |

| 现象 | 优先检查 |
|---|---|
| 增加子步后软度变化异常 | 是否用了整步 \(\Delta t\) 代替 \(h\) |
| 推开过猛 | bias符号、max夹限、是否重复乘scale |
| 静态接触数值对不上 | 是否遗漏频率夹限后的静态二倍 |
| 法向算完又接近 | 是否出现摩擦或其他约束的耦合反馈 |
| 速度稳定但位置不修正 | 是否在积分位置前就去掉纠偏速度 |

| 主题 | 源码入口 |
|---|---|
| 软度三系数和零频 | [`solver.h:238–280`](../src/solver.h#L238-L280) |
| 子步长度与频率夹限 | [`physics_world.c:956–980`](../src/physics_world.c#L956-L980) |
| 实际子步阶段 | [`solver.c:1082–1169`](../src/solver.c#L1082-L1169) |
| 分离、bias与软法向 | [`contact_solver.c:271–328`](../src/contact_solver.c#L271-L328) |
| Relax后半部分 | [`contact_solver.c:331–385`](../src/contact_solver.c#L331-L385) |
| 位置积分 | [`solver.c:114–158`](../src/solver.c#L114-L158) |

最后再看优化：固定准备数据、缓存几何和子步复用减少重复工作；宽向量与图着色属于执行组织，不改变本章每个公式的量纲和符号。

[返回总目录](./README.md) · [继续第12章](./12-接触求解器逐行导读与完整算例.md)
