  

The Financial Independence Retire Early (FIRE) movement has, for decades, sought to free itself of work by living frugally and investing a large share of its income to retire early and live off its invested savings. The most important factor in being able to FIRE is the number of years you have to compound your investments. Thus, an easy joke to make is "if only my grandfather had invested this money for me on the day i was born". 

This made me start thinking: How much money would I have to put down on the day my first child is born so they never have to think about retirement? As Einstein is famously misquoted as saying: 

> Compound interest is the strongest force in the universe

and giving my potential future child the ability to invest from birth is something they could never achieve on their own.

So let's say my child will need 2 million dollars for a comfortable retirement at age 65. They would never have to contribute towards this, the money would just be locked away when they are born in an international fund and then given to them on their 65th birthday. If we assume the average market return after inflation will be around 7%, as it has been historically, the amount of money I would have to put down would then be

$$   I_0 = I_f/(1 + R)^Y = (2dot 10^(6))/(1.07^(65)) = 24.608 "USD"$$

Not that bad! It is a lot of money, for sure, but not that much when you think of the security it would give to my child: they would never having to think about retirement, and never have to contribute towards it. Exponentials are really unintuitive, and it is impressive how much effect 65 years of compounding gives you. This is an interesting thought, but was if we took it a step further? 

## Going Generational
What if I invested for my grandchildren? For them, compounding would have an even greater effect, so I’d need to invest much less. If my child has my grandchild at age 30, my investment would need to be:

$$   I_("grandchild")= (2dot 10^(6))/(1.07^(65+30)) = 3.232 "USD" $$  
Now we are talking, this is not an insignificant amount of money, but it is definitely not a huge sum and it is only 13% of the money i needed before to secure retirement for my child. If we continue this though on to my grand-grandchild i would only need 425 dollars invested (1.7% of the money for my child).

The sum is getting smaller and smaller for every increase in the number of generations, and thus the total amount of money to secure their retirement is _converging_, i.e there exists a number which i could invest at the birth of my first child that would secure the retirement of all firstborns in my heritage in perpetuity. This we can generalise into the sum:  
$$ (2dot 10^(6))/(1.07^(65+30))+(2dot 10^(6))/(1.07^(65+60))+(2dot 10^(6))/(1.07^(65+90)) ... = sum_(n=0)^(infinity) I_"f"/((1+R)^(Y_r+Y_c n)) $$  
Now, if we take this sum and set $ N=infinity$ (or a very large number), we will find the amount of money I would need to invest to secure the entire heritage of firstborns. Using the above numbers, this becomes:  
$$ sum_(n=0)^(infinity) (2 dot 10^(6))/((1+0.07)^(65+30n)) = 28330 $$

Of course, this is only part of the story. Statistically, I am likely to have more than one child. My children, their children, and so on are also likely to have more, so we introduce $k$ to be the average number of kids me and my offsprings will have, and assume that it will be constant forever. Then the expression for the required initial investment will be:

$$ I_("total") = sum_(n=0)^∞ I_n = sum_(n=0)^∞ k^(n + 1) · M / (1 + R)^(Y + n Y_c) $$

If we then factor out the constants which are not dependent on $n$ 

$$ I_("total") = k M / (1 + R)^Y sum_(n=0)^∞ (k / (1 + R)^(Y_c))^n $$

And let $r = k / (1 + R)^(Y_c)$, then we get the geometrical series: 

$$ I_("total") = k M / (1 + R)^Y sum_(n=0)^∞ r^n $$  
The cool thing about geometric series in the form $sum_(n=0)^infinity r^n$, is that they converge if and only if $|r| < 1$. Thus, our series will converge (meaning there exists an amount of money that can fulfill the infinite retirements), if and only if:  
$$ k/(1 + R)^(Y_c) < 1 $$ 
Thus if we assume that we have $k=2$  kids per generation, 30 years between each generation $Y_c=30$, and a return of 7% $R=0.07$ then our convergence test yields:

$$ 2/(1 + 0.07)^(30) = 0.26 < 1 $$
And there is an amount of money that could solve our 

Okay, so let's just let that sink in.  
1. In this simple model of investment return, we have identified that for certain setups _it is_ possible to secure FIRE for all your future generations, achieving true generational wealth.  
2. There are only 3 factors that determine if it is possible.  
	1. The average number of children per generation  $k$
	2. The return on investment, $R$
	3. The average generational gap between being born and having a child, $Y_c$ 

