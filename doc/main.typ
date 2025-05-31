Compund interest is one of the most powerfull forces of the world...

This made me think; how much money would i have to invest at the birth of a potential child for the child to never have to think about retirement.

We will have some fundamental assumptions

+ The required pension amount $M$ will be deducted immediatly from the investment pool at retirement and does not acue interest after the pension has started

This made me realize: Wait is this a converging infinite sum? Is there an amount of money i can invest that would enable all my children and their offspring to retire early, i.e: FIRE for my dynasty? 


How much money is needed for a single child to 

$ M = B(1+R)^Y  $

Where $M$ is the amount of money at the end of the investment period, and B is the initial investment. Thus to obtain how much we need to invest for a given desired return, we can use a little algebra. 

$ B_("child") = M/(1+R)^Y $

If we assume that the retirement age in Denmark is $Y=72$ years, and a required amount of money saved is $M = 10.000.000"DKK"$ and the $R =7%$ ROI per year we get an invested amount

$ B_("child") = (10dot 10^6)/(1+0.07)^72 = $

So a decently low number. Very acheivable, really shows the power of compound interest. This made me think, with the compunding being exponential, how much would i have to invest for my grandchild to also get a retirement. This will require an additional investment, but it is going to be significantly less, since there will be even more time for the power of compund interest to go into effect. For a grandchil i will need the total sum $B_T$ being

$ B_T = B_("child") + B_("grandchild") $

The amount of extra time the grandchild will have to accue interest is 


So here convert the expression into a sum, and introduce another time factor which is the expected number of years between kids, i.e how old will my kid be when they have their own kid. We will call this $ Y_c $

$ B = sum_0 M/(1+R)^(Y_0 + n Y_c) $

If we assume a yearly average rate of return of 7% after inflation, and

$ M $

$ sum B_n = sum 2 M/(1+R) $

In a situation where there is no not p

$ sum B_n = sum_(n=0)^N k^n M/(1+R)^(Y + Y_c n) = M sum_(n=0)^N k^n 1/(1+R)^(Y + Y_c n) $



$ lr(|a_(n+1)/a_n|) = lr(|k^(n+1) 1/(1+R)^(Y_c (n+1)) * k^n 1/(1+R)^(Y_c n)|)  = lr(|c/(1+R)^(Y_c)|) < 1 $

$ lr(1/(1+R)^(Y_c)) < c $

$ Y_c < log_(1+R)(1/c) $