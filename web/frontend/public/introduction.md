The Financial Independence Retire Early (FIRE) movement has, for decades, sought to free itself of work by living frugally and investing a large share of its income to retire early and live off its invested savings. The most important factor in being able to FIRE is the number of years you have to compound your investments. Thus, an easy joke to make is "if only my grandfather had invested this money for me on the day I was born". 

This made me start thinking: How much money would I have to put down on the day my first child is born so they never have to think about retirement? As Einstein is famously misquoted as saying: 

> Compound interest is the strongest force in the universe

and giving my potential future child the ability to invest from birth is something they could never achieve on their own.

So let's say my child will need 2 million dollars for a comfortable retirement at age 65. They would never have to contribute towards this, the money would just be locked away when they are born in an international fund and then given to them on their 65th birthday. If we assume the average market return after inflation will be around 7%, as it has been historically, the amount of money I would have to put down would then be

$$I_0 = \frac{M}{(1 + R)^Y} = \frac{2 \times 10^{6}}{1.07^{65}} = 24{,}608 \text{ USD}$$

Not that bad! It is a lot of money, for sure, but not that much when you think of the security it would give to my child: they would never have to think about retirement, and never have to contribute towards it. Exponentials are really unintuitive, and it is impressive how much effect 65 years of compounding gives you. This is an interesting thought, but what if we took it a step further? 

## Going Generational
What if I invested for my grandchildren? For them, compounding would have an even greater effect, so I’d need to invest much less. If my child has my grandchild at age 30, my investment would need to be:

$$I_{\text{grandchild}} = \frac{2 \times 10^{6}}{1.07^{65+30}} = 3{,}232 \text{ USD}$$

Now we are talking — this is not an insignificant amount of money, but it is definitely not a huge sum, and it is only 13% of the money I needed before to secure retirement for my child. If we continue this thought on to my great-grandchild, I would only need 425 dollars invested (1.7% of the money for my child).

The sum is getting smaller and smaller for every increase in the number of generations, and thus the total amount of money to secure their retirement is _converging_, i.e. there exists a number that I could invest at the birth of my first child that would secure the retirement of all firstborns in my heritage in perpetuity. This we can generalise into the sum:

$$\frac{2 \times 10^{6}}{1.07^{65}}+\frac{2 \times 10^{6}}{1.07^{65+30}}+\frac{2 \times 10^{6}}{1.07^{65+60}} + \cdots = \sum_{n=0}^{\infty} \frac{M}{(1+R)^{Y+Y_c n}}$$

Now, if we sum this all the way to infinity (or a very large number of terms), we find the total amount of money I would need to invest to secure the entire heritage of firstborns. Using the above numbers, this becomes:

$$\sum_{n=0}^{\infty} \frac{2 \times 10^{6}}{(1+0.07)^{65+30n}} = 28{,}330$$

Of course, this is only part of the story. Statistically, I am likely to have more than one child. My children, their children, and so on are also likely to have more, so we introduce $k$ to be the average number of kids my offspring and I will have, and assume that it will be constant forever. Then the expression for the required initial investment will be:

$$I_{\text{total}} = \sum_{n=0}^{\infty} I_n = \sum_{n=0}^{\infty} \frac{k^{n + 1} \cdot M}{(1 + R)^{Y + n Y_c}}$$

If we then factor out the constants which are not dependent on $n$ 

$$I_{\text{total}} = \frac{k M}{(1 + R)^Y} \sum_{n=0}^{\infty} \left(\frac{k}{(1 + R)^{Y_c}}\right)^n$$

And let $r = \frac{k}{(1 + R)^{Y_c}}$, then we get the geometric series: 

$$I_{\text{total}} = \frac{k M}{(1 + R)^Y} \sum_{n=0}^{\infty} r^n$$

The cool thing about geometric series in the form $\sum_{n=0}^{\infty} r^n$ is that they converge if and only if $|r| < 1$. Thus, our series will converge (meaning there exists an amount of money that can fulfill the infinite retirements) if and only if:

$$\frac{k}{(1 + R)^{Y_c}} < 1$$

Thus if we assume that we have $k=2$ kids per generation, 30 years between each generation $Y_c=30$, and a return of 7% $R=0.07$, then our convergence test yields:

$$\frac{2}{(1 + 0.07)^{30}} = 0.26 < 1$$

And there is an amount of money that could be invested at the birth of my first child that would secure the retirement of all my descendants in perpetuity.

Okay, so let's just let that sink in.

1. In this simple model of investment return, we have identified that for certain setups _it is_ possible to secure FIRE for all your future generations, achieving _true generational wealth_.
2. There are only 3 factors that determine if it is possible.
	1. The average number of children per generation $k$
	2. The return on investment, $R$
	3. The average generational gap between being born and having a child, $Y_c$