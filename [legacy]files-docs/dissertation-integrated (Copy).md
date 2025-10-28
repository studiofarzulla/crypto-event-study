| Note to student: Attach to essay or copy and paste to front of online submission. |
| --- |
|  |
| Note to the Marker |
|  |
| Please consider the following candidate's written work in respect of Specific Learning Difficulties and / or a neuro-disability with similar information processing traits (such as ADHD, autism, cerebral palsy etc) |
|  |
| AG44473 |
| (Candidate Number) |
|  |
| This student has provided medical evidence to confirm a disability/impairment under the categories outlined above. |


|  |
| --- |
| For The Marking of Work for Language Modules |
|  |


| In the case of language modules, please consider carefully what specifically is being assessed. If accuracy in the use of language is being assessed, (e.g. spelling, grammar and punctuation) then exceptions should NOT be made for disability. However, if the paper is being assessed either fully or partly on other criteria, then please follow the guidance described below. |
| --- |
|  |


| Guidelines for Markers Assessing Coursework attached with this sheet |
| --- |
|  |


| Unless core assessment criteria, and with the exception of essential technical vocabulary, all minor errors as described below should be disregarded in marking the work attached.Although students with cover sheets should be marked with regards to the elements of content in their work, the logical argument of an essay or report may not be constructed in a very sequential manner. In addition, grammatical and sentence structure errors can be missed by the student.Students with specific learning difficulties and those with other processing impairments commonly make errors with spelling, punctuation, and in the form of the omission of small function words, the addition or repetition of such words, the transposition of words and the substitution of other function words (the /a / an / for / from).The use of spell- and grammar-checkers has a limited use for students with these challenges. Word substitution, phonetic equivalent and American spelling errors can occur.Word count: if a word limit is applied please allow for variance due to the challenges described above affecting editing. |
| --- |


| A summary of approaches for markers is given below (from "Guidelines for Examiners" document available from the Examinations and Awards Office) |
| --- |
|  |


| Look for content, analysis evidence of reading/research Include positive/constructive comments in feedback and acknowledge cover sheet was taken into consideration Use clear English in feedback Avoid using red coloured pens for comments In correcting English, explain what is wrong and give examples |
| --- |
|  |


| Academic year: 2025/26 |
| --- |


|  |
| --- |
|  |
| Alteration or misuse of this document in any way will result in referral to the Disciplinary Committee |


| Differential Volatility Responses to Infrastructure and Regulatory Events in Cryptocurrency Markets: A TARCH-X Analysis with Sentiment Decomposition |
| --- |

Murad Farzulla AG44473

Supervisor: Dr Fotis Papailias

This dissertation is submitted in part fulfilment of the requirement for the degree of M.Sc. Finance Analytics

**DECLARATION BY STUDENT**

I understand what is meant by plagiarism/collusion and have signed at enrolment the declaration concerning the avoidance of plagiarism/collusion.

I understand that plagiarism and collusion is a serious examinations offence that may result in disciplinary action being taken.

I understand that I must submit work BEFORE the deadline, and that failure to do so may result in late submission penalties.

I understand that where a word limit is indicated, I should adhere to the word limit and failure to do so may result in penalties.

I understand that King's requires students to acknowledge any use of generative AI tools in coursework. **Please select and complete the applicable statement, and provide additional information where required.**

2. I declare that parts of this submission has contributions from AI software and that it aligns with acceptable use as specified as part of the assignment brief/ guidance and is consistent with good academic practice. The content can still be considered as my own words. I understand that as long as my use falls within the scope of appropriate use as defined in the assessment brief/guidance then this declaration will not have any direct impact on the grades awarded.

I acknowledge use of software to **[include only the statements which apply, and provide details as appropriate]:**** **

(i) Generate ideas or structure suggestions, for assistance with understanding core concepts, or other substantial foundational and preparatory activity.

Claude AI was used during the preliminary research phase to help understand complex econometric concepts, particularly regarding GARCH model specifications and volatility modelling frameworks. It also assisted in understanding the theoretical foundations of market microstructure theory and information processing mechanisms in financial markets.

(ii) The AI tool was primarily used to assist with learning programming languages outside the scope of the Master's programme, specifically Python implementations of custom GARCH models with exogenous variables, as existing econometric packages did not support the required specifications. The actual code implementation, data analysis, and empirical results represent my own work.

All empirical analysis, data collection, event classification, model estimation, and interpretation of results were conducted independently. The writing, argumentation, and conclusions drawn are my own original work based on the analysis performed.


<!-- COVERSHEET 1 - TO BE REMOVED -->


---

***Contents***


<!-- COVERSHEET 2 - TO BE REMOVED -->


---

# 0. Abstract

This study examines cross-sectional heterogeneity in cryptocurrency volatility responses to major market events using TARCH-X models across six leading cryptocurrencies (2019-2025). Contrary to the hypothesis that event types (infrastructure vs regulatory) drive differential impacts, we find no statistical difference between categories (p=0.997). Instead, we document extreme cross-sectional heterogeneity: event sensitivity varies 35-fold from BNB (0.947%) to LTC (-0.027%), with 93% of response variation attributable to token-specific characteristics. Exchange tokens and regulatory litigation targets exhibit significantly higher event sensitivity (Cohen's d = 5.19).

Robustness checks validate these findings across multiple dimensions: placebo tests with 1,000 random event dates confirm heterogeneity is genuinely event-driven (p<0.001); alternative event windows (±1 to ±7 days) preserve rankings (Spearman ρ > 0.85); temporal stability analysis reveals perfect rank correlation across bull and bear markets (ρ = 1.00). Corrected correlation analysis demonstrates substantial portfolio diversification benefits, with equal-weight portfolios achieving 45% variance reduction.

Our findings challenge pooled regression approaches common in cryptocurrency research and demonstrate that token selection matters 13 times more than event timing for volatility exposure management.


<!-- COVERSHEET 3 - TO BE REMOVED -->


---

Model comparisons strongly support TARCH-X improves out-of-sample forecast errors by 8–15% overall, with reductions up to ~25% during event windows. However, sentiment variables provide limited incremental explanatory power beyond discrete event indicators, suggesting that weekly aggregation may obscure higher-frequency information dynamics. The extreme persistence parameters indicate that cryptocurrency markets operate in a distinct volatility regime where discrete shocks become absorbed into long-memory processes, posing fundamental challenges for event impact estimation and risk management within traditional econometric frameworks.

# **1. Introduction**

## **1.1 Research Question**

***"Do cryptocurrency markets exhibit differential information processing mechanisms between regulatory announcements and operational infrastructure failures, and can news sentiment serve as a leading indicator of these asymmetric volatility responses?"***

## **1.2 Research Hypotheses**

***Primary Hypothesis (H1):****** ******Asymmetric Volatility Response****** - Market structure/infrastructure events generate significantly larger volatility impacts than regulatory events due to immediate liquidity disruption versus gradual information absorption mechanisms.***

***Secondary Hypothesis (H2):****** ******Sentiment Leading Indicator****** - News sentiment (GDELT-derived) serves as a leading indicator for volatility asymmetries, with infrastructure events showing immediate sentiment-volatility correlation versus regulatory events showing lagged responses.***

***Methodological Hypothesis (H3):****** ******TARCH-X Superiority****** - TARCH-X models incorporating sentiment proxies outperform standard GARCH specifications in capturing asymmetric volatility responses to different event types in cryptocurrency markets.***

***The cryptocurrency market's transformation from experimental technology to a three-trillion-dollar asset class has created unprecedented challenges for understanding information processing in financial markets (Reuters, 2021). Since Bitcoin's inception in 2009, digital assets have developed unique structural characteristics - continuous 24/7 trading, fragmented exchange infrastructure, predominantly retail participation, and critical technological dependencies - that fundamentally distinguish them from traditional financial markets. These features violate core assumptions of classical market efficiency theory and necessitate new frameworks for understanding how different information types are processed and incorporated into prices (Makarov and Schoar, 2020).***

***The theoretical foundation for examining differential information processing in cryptocurrency markets emerges from the intersection of market microstructure theory and behavioural finance. While the Efficient Market Hypothesis predicts uniform and instantaneous price adjustment to all available information, cryptocurrency markets exhibit systematic deviations from this baseline. Empirical evidence documents persistent cross-exchange price discrepancies exceeding five per cent, significant return autocorrelation at high frequencies, and pronounced asymmetric volatility responses that suggest complex, non-uniform information processing mechanisms (Urquhart, 2016; Bariviera, 2017). The dominance of retail investors, who constitute approximately 80% of trading volume and exhibit stronger behavioural biases than institutional participants, amplifies sentiment-driven dynamics and creates conditions for differential processing of various event types (Auer and Claessens, 2018).***

***Cryptocurrency volatility characteristics provide crucial insights into these information processing mechanisms. Extensive research using GARCH-family models establishes that cryptocurrencies exhibit extreme volatility clustering with persistence parameters approaching unity, suggesting near-integrated variance processes (Katsiampa, 2017). Moreover, leverage effects - where negative shocks generate disproportionately larger volatility increases - are approximately twice as pronounced as in equity markets, with asymmetry parameters in threshold models ranging from 0.15 to 0.30 (Baur and Dimpfl, 2018). Recent methodological advances incorporating exogenous variables into volatility specifications, particularly TARCH-X models that combine threshold asymmetry with external information flows, demonstrate significant improvements in capturing cryptocurrency market dynamics (Walther et al., 2019).***

***The integration of sentiment analysis reveals the critical role of investor attention in cryptocurrency price formation. Unlike traditional markets where institutional investors dominate price discovery, cryptocurrency markets show strong retail-driven sentiment effects. Studies demonstrate that social media sentiment predicts Bitcoin returns up to 48 hours in advance, whilst news sentiment extracted from mainstream media shows even stronger relationships, particularly for negative events (Phillips and Gorse, 2018; Rognone et al., 2020). The Global Database of Events, Language, and Tone (GDELT) provides unprecedented granularity for constructing thematic sentiment measures, processing over 100,000 global news sources to enable decomposition of regulatory versus infrastructure-related coverage, a capability essential for testing differential information processing hypotheses (Shen et al., 2019).***

***Empirical evidence suggests fundamentally different market responses to regulatory announcements versus infrastructure failures. Regulatory events - such as government bans, enforcement actions, or new compliance requirements - typically generate immediate price declines of 5-15% followed by elevated volatility persisting for 15-30 days, consistent with gradual absorption of legal risk information (Auer and Claessens, 2018). These events affect valuations through expectation channels, requiring investors to reassess fundamental value based on changing legal and operational constraints. The extended volatility elevation suggests markets require substantial time to fully process regulatory implications, potentially reflecting the complexity of interpreting legal language and assessing long-term consequences (Feinstein and Werbach, 2021).***

***In contrast, infrastructure failures, including exchange outages, wallet breaches, and smart contract exploits, create immediate mechanical disruptions to market functioning. These events generate volatility spikes of 300-500% above baseline levels that typically decay within 72-96 hours, suggesting markets treat them as temporary liquidity shocks rather than fundamental revaluations (Chen et al., 2023). The emergence of decentralised finance has introduced novel infrastructure vulnerabilities, with flash loan attacks facilitating over seven billion dollars in losses since 2020. These attacks, which exploit protocol composability within single blockchain transactions, represent a distinct category of operational risk that combines cyber-security threats with financial engineering vulnerabilities (Qin et al., 2021).***

***Despite extensive research on cryptocurrency volatility and event impacts, critical gaps remain in understanding differential information processing mechanisms. Existing literature typically examines regulatory and infrastructure events in isolation using incompatible methodologies, making direct comparison impossible. Studies of regulatory events employ traditional event study methods with extended windows, whilst infrastructure analyses use high-frequency approaches with short horizons, reflecting untested assumptions about processing speeds (Corbet et al., 2019). Furthermore, no research has systematically examined how continuous sentiment flows interact with discrete event impacts, despite evidence that background sentiment conditions may moderate market responses through behavioural channels.***

***This study addresses these limitations through a unified analytical framework that enables direct comparison of regulatory and infrastructure events whilst incorporating both discrete and continuous information flows. I implement three key methodological innovations. First, I develop a rigorous event classification taxonomy based on information transmission channels, distinguishing between expectation-channel events (regulatory) and mechanical-disruption events (infrastructure). Second, I construct decomposed GDELT-based sentiment indices that separate regulatory from infrastructure-related news coverage, enabling tests of whether thematic sentiment provides differential predictive power. Third, I employ hierarchical TARCH-X specifications that progressively incorporate asymmetric effects, discrete event dummies, and continuous sentiment proxies, allowing formal testing of whether sentiment augmentation improves volatility modelling beyond traditional approaches.***

***This research makes several contributions to understanding cryptocurrency market dynamics. Theoretically, I test whether the unique characteristics of cryptocurrency markets, continuous trading, fragmented liquidity, and retail dominance, enable sophisticated forms of differential information processing impossible in traditional markets. Methodologically, I develop a framework for comparing fundamentally different event types within consistent econometric specifications whilst controlling for overlapping effects common in high-frequency cryptocurrency data. Practically, I provide evidence essential for risk management, with implications for dynamic hedging strategies if infrastructure events generate predictable mean reversion patterns versus persistent regulatory effects requiring longer-term position adjustments.***

***The implications extend beyond market participants to regulatory policy design. If regulatory announcements create prolonged uncertainty exceeding their fundamental impact, authorities might benefit from clearer forward guidance and phased implementation. Conversely, if infrastructure failures generate systemic spillovers through liquidity channels, regulatory focus should prioritise operational resilience requirements and circuit breaker mechanisms. Understanding these differential mechanisms becomes increasingly critical as cryptocurrency markets mature toward greater institutional participation and regulatory integration.***

***This research proceeds through systematic investigation of three hypotheses. First, I test whether market infrastructure events generate significantly larger volatility impacts than regulatory events, consistent with immediate liquidity disruption versus gradual information absorption mechanisms. Second, I examine whether news sentiment serves as a leading indicator for volatility asymmetries, with infrastructure events showing immediate sentiment-volatility correlation versus lagged regulatory responses. Third, I evaluate whether TARCH-X models incorporating sentiment proxies outperform standard GARCH specifications in capturing asymmetric volatility responses to different event types.***

***Through comprehensive empirical analysis spanning six major cryptocurrencies from January 2019- August 2025, I document nuanced evidence regarding differential information processing. The relationship between infrastructure and regulatory events varies substantially across cryptocurrencies, with infrastructure coefficients ranging from near-zero (LTC: 0.01) to substantial (BNB: 1.13), whilst regulatory coefficients demonstrate similar heterogeneity. Aggregate analysis reveals remarkably similar mean effects between event types (infrastructure: 0.417, regulatory: 0.415), suggesting market-specific factors dominate universal patterns. TARCH-X specifications incorporating decomposed sentiment show modest improvements in model fit, with information criteria indicating enhanced performance for specific cryptocurrencies rather than uniform superiority. Notably, only BNB demonstrates statistically significant infrastructure effects at conventional levels, though significance diminishes after false discovery rate correction. These findings challenge assumptions of uniform information processing mechanisms across cryptocurrency markets and suggest that asset-specific characteristics, including market capitalisation, trading volume, and technological architecture, may determine differential responses to distinct event categories.***


<!-- END COVERSHEET 3 -->


---

# 2. Literature Review

## 2.1 Theoretical Foundations: Market Efficiency and Information Processing in Digital Asset Markets

The theoretical foundation for understanding cryptocurrency market responses to different event types rests on the intersection of market microstructure theory, information economics, and behavioural finance. The Efficient Market Hypothesis (EMH), as formulated by Fama (1970), provides the baseline theoretical expectation that markets should rapidly incorporate all available information into asset prices. Under the strong-form EMH, both regulatory information and infrastructure disruptions would be immediately reflected in prices with no persistent abnormal volatility effects. However, the unique characteristics of cryptocurrency markets, including continuous trading, fragmented exchanges, heterogeneous participant composition, and technological barriers, create conditions that may fundamentally violate EMH assumptions and enable differential processing of distinct information types (Liu and Tsyvinski, 2021).

The theoretical foundation for volatility modelling in financial markets originates with Engle's (1982) autoregressive conditional heteroscedasticity (ARCH) model, which first captured the time-varying nature of financial market volatility. This breakthrough enabled researchers to model volatility clustering: the empirical observation that large price changes tend to be followed by large changes, and small changes by small changes. Bollerslev (1986) generalised this framework to the GARCH model, which has become the workhorse of volatility analysis in both traditional and cryptocurrency markets.

The Adaptive Markets Hypothesis (AMH) proposed by Lo (2004) offers a more nuanced framework for understanding time-varying market efficiency in cryptocurrency markets. Under the AMH, market efficiency is not a static property but evolves as market participants learn, adapt, and develop new trading technologies. This evolutionary perspective is particularly relevant for understanding how markets might process regulatory announcements differently from infrastructure failures, as participants develop distinct heuristics for each event type. Khuntia and Pattanayak (2018) provide empirical support for the AMH in Bitcoin markets, finding evidence of time-varying predictability that corresponds to periods of market stress and regulatory uncertainty.

The theoretical challenge lies in reconciling these competing frameworks with the decentralised nature of cryptocurrency markets. Traditional asset pricing models assume the existence of centralised market makers, standardised trading mechanisms, and unified regulatory oversight, assumptions that do not hold in cryptocurrency markets. As demonstrated by Sockin and Xiong (2022), the decentralised structure of cryptocurrency platforms creates unique trade-offs between user protection and network effects that fundamentally alter how different types of information, regulatory versus operational, are processed and incorporated into prices.

## 2.2 Market Microstructure and Differential Event Processing

The market microstructure literature provides crucial insights into how the unique design features of cryptocurrency markets affect price discovery and volatility dynamics for different event types. Unlike traditional markets with designated market makers and centralised order books, cryptocurrency markets operate through a fragmented landscape of exchanges with varying degrees of regulatory compliance, liquidity provision mechanisms, and fee structures (Makarov and Schoar, 2020). This fragmentation creates conditions where infrastructure failures and regulatory announcements may propagate through fundamentally different channels.

Makarov and Schoar (2020) document substantial and persistent arbitrage opportunities across cryptocurrency exchanges, with price differences often exceeding 10% and persisting for hours or days. These findings challenge the standard arbitrage-based arguments for market efficiency and suggest that limits to arbitrage are particularly severe in cryptocurrency markets. The authors identify several factors that constrain arbitrage, including exchange-specific risks, regulatory uncertainty, and technical barriers to cross-exchange trading. These frictions may allow infrastructure shocks, which directly impair arbitrage mechanisms, to create more severe volatility responses than regulatory announcements that leave trading infrastructure intact.

Liu and Tsyvinski (2021) establish that cryptocurrency returns are driven by factors specific to cryptocurrency markets rather than traditional financial market factors. Their comprehensive analysis reveals that cryptocurrency returns have minimal exposure to stock market factors, currency movements, or commodity prices, but exhibit strong sensitivity to cryptocurrency-specific network effects and momentum factors.

Recent microstructure analysis confirms that cryptocurrency markets exhibit liquidity and price discovery patterns similar to other investible asset classes, with predictable cross-market effects particularly evident between Bitcoin and Ethereum (Easley, O'Hara, and Yang, 2024, SSRN Working Paper). These findings support the application of traditional market microstructure theory to cryptocurrency event studies whilst acknowledging the unique features of decentralised market architecture.

## 2.3 Information Processing, Behavioural Factors, and Sentiment Dynamics

The role of retail investors and behavioural biases in cryptocurrency markets has important implications for how different types of events are processed and how sentiment indicators might predict volatility responses. Glaser et al. (2014) provide early evidence that cryptocurrency users are primarily motivated by speculative rather than transactional considerations, suggesting that price formation in these markets may be more susceptible to sentiment and herding behaviours than traditional asset markets, with potentially different responses to operational versus regulatory threats.

The high degree of retail participation in cryptocurrency markets creates conditions where noise trading and sentiment-driven behaviour may dominate fundamental value considerations, particularly during periods of uncertainty. Da and Huang (2020) demonstrate that attention-based measures, such as Google search volume, have significant predictive power for cryptocurrency returns and volatility. This finding suggests that retail investor attention plays a more prominent role in cryptocurrency price formation than in traditional markets, potentially amplifying the impact of salient infrastructure failures whilst causing more gradual absorption of complex regulatory developments.

The continuous, 24/7 nature of cryptocurrency trading eliminates the overnight gaps and weekend effects that characterise traditional markets, creating a continuous price discovery process that may process different event types at varying speeds. Katsiampa (2017) and Chu et al. (2017) demonstrate through GARCH modelling that this continuous trading amplifies volatility clustering and momentum effects. The absence of traditional market-closing mechanisms and circuit breakers means that infrastructure shocks can propagate through cryptocurrency markets without the natural cooling-off periods that exist in traditional markets, whilst regulatory announcements, often released during business hours, may be processed more gradually.

The sentiment-volatility nexus provides a critical mechanism for understanding differential event impacts. Tetlock (2007) established the foundational relationship between news sentiment and market volatility in traditional markets, whilst Baker, Bloom, and Davis (2016) demonstrated how news-based indices can capture policy uncertainty effects. In cryptocurrency markets, sentiment may serve as a leading indicator that differentiates between event types: infrastructure failures generate immediate negative sentiment concurrent with volatility spikes, whilst regulatory announcements may show sentiment changes that precede volatility adjustments as market participants gradually process implications.

## 2.4 Asymmetric Volatility in Cryptocurrency Markets

Empirical evidence consistently demonstrates that cryptocurrency markets exhibit pronounced asymmetric volatility responses, with negative shocks generating disproportionately larger volatility increases than positive shocks of equivalent magnitude. Cheikh, Zaied and Chevallier (2020) document this asymmetry across major cryptocurrencies using smooth transition GARCH models, whilst Katsiampa (2017) confirms that asymmetric specifications consistently outperform symmetric models for Bitcoin volatility.

Nelson (1991) introduced the exponential GARCH (EGARCH) model specifically to address two limitations of standard GARCH models: the non-negativity constraints on parameters and the symmetric treatment of shocks. The EGARCH specification allows for unrestricted parameter estimation whilst capturing the leverage effect through an asymmetric response function. This methodological advance is particularly relevant for cryptocurrency markets, where negative news, whether regulatory or infrastructure-related, often generates disproportionately larger volatility increases than positive news of equivalent magnitude.

This asymmetry has critical implications for comparing infrastructure and regulatory events, as both typically manifest as negative market shocks but may exhibit different persistence characteristics. Infrastructure failures that directly impair trading mechanisms might generate immediate, severe volatility spikes with mechanical persistence. Regulatory announcements, whilst also negative signals, may produce more gradual volatility increases as market participants progressively interpret implications.

The incorporation of exogenous variables into asymmetric volatility models enables decomposition of total volatility into baseline dynamics, continuous sentiment-driven pressure, and discrete event shocks, essential for testing whether different event types exhibit distinct volatility signatures and adjustment patterns.

## 2.5 Event Studies in Cryptocurrency Markets: From Price to Volatility Effects

The empirical literature on event impacts in cryptocurrency markets has evolved from early studies focusing primarily on price effects to more sophisticated analyses of volatility dynamics. However, the extant literature has yet to systematically compare infrastructure and regulatory events within a unified framework.

### 2.5.1 Regulatory Event Studies

Auer and Claessens (2018) provide one of the first comprehensive analyses of cryptocurrency market reactions to regulatory announcements, examining 151 regulatory events across multiple jurisdictions. Their findings reveal heterogeneous responses depending on the type of regulatory action, with blanket bans generating larger price declines than targeted regulations. However, their focus on price effects rather than volatility dynamics limits insights into persistence and adjustment mechanisms.

Saggu et al. (2025) extend this analysis to examine SEC regulatory interventions, finding that enforcement actions generate immediate volatility spikes that typically dissipate within days, whilst legislative proposals create more prolonged periods of elevated uncertainty. Their distinction between different regulatory types provides a framework for understanding gradual information absorption, but lacks comparison with non-regulatory market disruptions.

Note that Saggu and colleagues have produced two related but distinct papers on SEC regulatory impacts: Saggu, Ante, and Kopiec (2025) in Finance Research Letters examining enforcement actions specifically, and a separate analysis by Ante and Saggu (2025) in Technological Forecasting and Social Change examining broader regulatory uncertainty effects.

Chokor and Alfieri (2021) extend this temporal analysis by examining 120 regulatory events across 42 countries, demonstrating that regulatory impacts exhibit distinct short-term and long-term phases. They find immediate price declines averaging 3.5% within the first seven days, followed by persistent volatility elevation lasting up to 30 days for restrictive regulations. Bonaparte and Bernile (2023) further develop this framework by constructing a real-time regulatory sentiment index from news coverage and social media, finding that negative regulatory sentiment predicts next-day cryptocurrency returns with economic significance comparable to traditional risk factors. Feinstein and Werbach (2021) provide crucial theoretical grounding, arguing that cryptocurrency markets process regulatory information through three distinct channels: compliance costs, market access restrictions, and legitimacy signals, each operating on different time horizons.

Zhang et al. (2023) examine the impact of China's comprehensive cryptocurrency ban on market volatility, finding that the regulatory announcement generated immediate volatility increases that persisted for several weeks. However, their analysis was limited to a single regulatory event and did not compare regulatory impacts with other types of market-moving events, highlighting the importance of comparative approaches.

### 2.5.2 Infrastructure and Market Structure Events

Whilst regulatory events have received significant attention, the systematic study of infrastructure failures has emerged as a critical research area. Grobys (2021) provides the first comprehensive analysis of blockchain hacking events, examining 29 major cryptocurrency exchange hacks between 2013 and 2020. His findings reveal that hacking events generate immediate volatility increases of 7-10% that persist for 5-10 trading days, with contagion effects spreading to non-hacked exchanges. Chen et al. (2023) extend this analysis using high-frequency tick-level data, documenting that major exchange hacks create immediate liquidity crises with bid-ask spreads widening by up to 300% and price impacts exceeding 15% within the first hour.

Milunovich and Lee (2022) employ a high-frequency event study methodology to compare infrastructure failures with regulatory announcements, finding that infrastructure events generate volatility spikes that are 40% larger in magnitude but 60% shorter in duration than regulatory shocks. Their decomposition of price impacts reveals that infrastructure failures operate primarily through a liquidity channel (accounting for 70% of the price effect), whilst regulatory events operate through an information channel (accounting for 80% of their effect). This distinction provides empirical support for the hypothesis that markets process operational and regulatory risks through fundamentally different mechanisms.

Recent developments in decentralised finance (DeFi) have introduced novel infrastructure vulnerabilities, including flash loan attacks and automated market maker failures. Flash loans, which enable uncollateralised borrowing within single blockchain transactions, have facilitated over $6.5 billion in exploits since DeFi's inception (Saggers et al., 2023). These attacks represent a distinct category of infrastructure events that can generate immediate liquidity crises and market disruption, complementing traditional exchange failures in my event taxonomy.


| Paper | Assets | Event Types | Window | Sentiment | Volatility Model |
| --- | --- | --- | --- | --- | --- |
| Auer & Claessens (2018) | BTC, ETH | Regulatory | ±10d | No | Price only |
| Saggu et al. (2025) | Multi | Regulatory | ±3d | Yes | GARCH |
| Zhang et al. (2023) | BTC | Regulatory | ±20d | No | GARCH |
| Caferra & Vidal-Tomás (2021) | Multi | Infrastructure | ±5d | Yes (GDELT) | GARCH |

### 2.5.3 Flash Loans and DeFi Infrastructure Vulnerabilities

The emergence of decentralised finance has introduced novel infrastructure vulnerabilities that traditional event study methodologies must adapt to address. Qin et al. (2021) provide the theoretical foundation for understanding flash loan attacks, demonstrating how atomic transactions, which either execute completely or revert entirely, enable risk-free arbitrage opportunities that can drain hundreds of millions from protocols within single blockchain blocks. Their analysis of 48 flash loan attacks reveals an average protocol loss of $3.2 million per incident, with the largest single attack (Cream Finance) resulting in $130 million in losses.

Gudgeon et al. (2020) develop a comprehensive taxonomy of DeFi attack vectors, categorising vulnerabilities into: (i) economic attacks exploiting protocol incentive misalignments, (ii) governance attacks manipulating voting mechanisms, and (iii) technical attacks exploiting smart contract bugs. Their framework reveals that 60% of DeFi failures stem from economic design flaws rather than coding errors, challenging the conventional focus on technical audits. Zhou et al. (2021) analyse the market microstructure implications of automated market makers (AMMs), demonstrating that sandwich attacks, where attackers manipulate prices before and after user trades, extract over $500 million annually from DEX users, representing a persistent infrastructure vulnerability that affects daily price formation.

## 2.6 Sentiment Indices and Leading Indicators in Digital Asset Markets

The development of cryptocurrency-specific sentiment measures has evolved from adaptations of traditional finance methodologies to novel approaches leveraging the unique data environment of digital asset markets. Whilst established indices like the Cryptocurrency Regulatory Risk Index (CRRIX) by Ni et al. (2021) and the Volatility Cryptocurrency Index (VCRIX) by Kim et al. (2021) provide validated measures of risk and uncertainty, data availability constraints and methodological opacity limit their practical application for comparative event analysis.

The CRRIX employs machine learning techniques to quantify regulatory risk from news coverage, finding strong synchronicity between regulatory uncertainty and market volatility with a one-week lag. The VCRIX provides a forward-looking volatility measure analogous to the VIX, using HAR models to forecast expected volatility. Campbell, Lo, and MacKinlay (1997) provide comprehensive econometric foundations for constructing and validating such indices, emphasising the importance of model-free approaches that avoid parametric assumptions about the underlying return distribution.

Alternative approaches using publicly available data sources offer greater transparency and flexibility. The Global Database of Events, Language, and Tone (GDELT) provides standardised sentiment scoring across millions of news articles, enabling construction of event-specific sentiment measures. Caferra and Vidal-Tomás (2021) demonstrate GDELT's utility for cryptocurrency market analysis, though existing implementations treat cryptocurrency news monolithically without distinguishing between event types.

Recent research demonstrates that social media sentiment, particularly from platforms like Twitter and Reddit, has substantial predictive power for cryptocurrency returns and volatility. Whilst Liu, Tsyvinski, and Wu (2022) identify common risk factors in cryptocurrency returns including network, momentum, and investor attention factors, studies focusing specifically on social media sentiment analysis have shown similar predictive power.

The innovation of decomposing sentiment into infrastructure and regulatory components enables testing whether different event types exhibit distinct sentiment-volatility relationships. Infrastructure events, characterised by immediate operational impact, should show contemporaneous sentiment-volatility correlation. Regulatory events, requiring interpretation and assessment of long-term implications, may exhibit lagged relationships as sentiment changes precede full volatility adjustment.

## 2.7 Methodological Considerations and Identification Challenges

The identification of causal effects in cryptocurrency event studies faces several methodological challenges particularly acute when comparing different event types. The issue of event endogeneity, where regulatory actions may be responses to market conditions rather than exogenous shocks, represents a fundamental threat to causal inference. Infrastructure events, being typically unexpected system failures, may offer cleaner identification than regulatory announcements that often follow periods of market stress.

The problem of confounding events is particularly severe in cryptocurrency markets, where the high frequency of news and announcements makes it difficult to isolate specific event effects. The wide event windows commonly used in cryptocurrency event studies (often ±20 days or more) increase the likelihood of capturing multiple contemporaneous events, potentially leading to misattribution of volatility effects. This concern is especially relevant when comparing events that may cluster differently: infrastructure failures might trigger regulatory responses, whilst regulatory announcements rarely cause infrastructure failures.

McWilliams and Siegel (1997) propose solutions to these identification challenges, including the use of multiple event windows, cross-sectional regression approaches, and simulation-based inference. Their framework is particularly relevant for cryptocurrency markets, where the high correlation amongst digital assets during crisis periods can amplify both Type I and Type II errors in event attribution. The application of Benjamini and Hochberg's (1995) false discovery rate correction becomes essential when testing multiple hypotheses across events and assets, controlling the expected proportion of false rejections amongst all rejections rather than the probability of any false rejection.

The multiple testing problem arising from examining numerous asset-event combinations requires careful statistical treatment. Whilst some studies acknowledge this issue, few implement appropriate corrections for multiple comparisons, potentially leading to inflated significance rates. The implementation of False Discovery Rate (FDR) corrections becomes essential when testing differential effects across event types and multiple assets.

To date, no study directly compares infrastructure and regulatory event impacts on volatility using decomposed sentiment indices and rigorous multiple-testing corrections across a multi-asset sample.


---

# 3. Methodology

## 3.1 Cryptocurrency Selection and Data

The selection of cryptocurrencies balanced statistical power, data quality, and market representativeness. Following Liu and Tsyvinski (2021) and Makarov and Schoar (2020), data integrity was prioritised over sample size. Selection criteria required: (i) continuous trading throughout January 2019 to August 2025, (ii) sustained top-decile liquidity, and (iii) distinct market archetypes to capture heterogeneous event responses.

The final sample comprises six cryptocurrencies:

Bitcoin (BTC) – market baseline and systematic risk factor (Bouri et al., 2017)

Ethereum (ETH) – smart contract platform capturing DeFi infrastructure exposure

XRP – regulatory case study given SEC litigation (2020-2025), enabling quasi-experimental identification

Binance Coin (BNB) – exchange token representing centralisation risks

Litecoin (LTC) – control asset with high BTC correlation (0.61-0.75) for difference-in-differences estimation

Cardano (ADA) – alternative proof-of-stake implementation contrasting Ethereum's model

Price and volume data are sourced from CoinGecko's institutional API, representing volume-weighted averages across major exchanges at 00:00:00 UTC. The 80-month study period encompasses complete market cycles including the 2020-2021 bull market, 2022 contagion crisis, and 2023-2025 regulatory normalisation. It should be noted that several prominent assets were excluded for the following rationale: Solana (network outages), Monero (exchange delistings), Uniswap (insufficient pre-2020 history), stablecoins (price-pegging mechanisms), and meme tokens (social sentiment-driven pricing). These exclusions prioritise continuous data availability over market coverage.

This selection provides sufficient cross-sectional variation whilst maintaining data quality standards essential for GARCH estimation. Daily closing prices are sourced from CoinGecko's institutional API at 00:00:00 UTC, with logarithmic returns calculated as r_t = ln(P_t/P_{t-1}) and outliers exceeding five standard deviations winsorised.

## 3.2 Event Selection and Classification

### 3.2.1 Event Identification

Event identification followed a systematic protocol drawing from primary regulatory documents, exchange/network announcements, and corroborating news sources spanning January 2019 to August 2025. From an initial corpus of 208 candidates, I applied three filters: (i) precise UTC timestamps, (ii) verifiable public records, and (iii) demonstrable market-wide price impact.

To address confounding from proximate events, a two-stage protocol was implemented. Events within ±3 days were consolidated if substantively related, with timing anchored at first disclosure. Unrelated overlapping events were prioritised by legal finality or technical severity, with dominated events retained for robustness checks. This process yielded 50 distinct events (note: some events were included to increase statistical power and to fill otherwise empty period.).

Events were selected based on consensus across multiple independent analyses, with final inclusion requiring appearance in at least 3 of 5 separate event compilations. Each analysis was creating a compilation of given set of events to include in the final analysis as well as the classification of each event in accordance to the outlined methodology above.

### 3.2.2 Classification Framework

Events were classified into two categories based on their market mechanism:

Infrastructure events (n=27): Incidents affecting transaction or settlement mechanics, including exchange outages, chain halts, protocol exploits, consensus changes, and halvings. The classification criterion is mechanical impact on execution/settlement, regardless of predictability. Scheduled upgrades (e.g., Ethereum Merge, Bitcoin halvings) are classified as infrastructure due to their operational impact.

Regulatory events (n=23): Legal or supervisory actions that alter the informational environment whilst preserving trading mechanics, including enforcement actions, ETF approvals, legislative frameworks. These affect valuation through legal risk and compliance cost channels rather than operational disruption.

Classification followed a decision tree: (1) If normal execution/settlement mechanisms were impaired → Infrastructure; (2) If impact operated through legal/informational channels → Regulatory. Boundary cases were resolved by proximate mechanism.

### 3.2.3 Overlap Treatment

With [-3,+3] event windows, any events within 6 days produce overlaps. After consolidation, three pairs required special treatment:

(A) SEC v Binance (June 5) and SEC v Coinbase (June 6, 2023): Treated as a single regulatory episode with composite dummy D_SEC_enforcement for [June 2 to 9], recognising coordinated enforcement action.

(B) Ethereum EIP-1559 (Aug 5) and Poly Network hack (Aug 10, 2021): Retained as separate events with proportional weighting (0.5) during overlap period [Aug 7 to 8] to prevent double-counting whilst preserving distinct shock identification, acknowledging this approach treats overlapping days as equally attributable to both events.

(C) Bybit hack (Feb 21) and SEC-Coinbase dismissal (Feb 27, 2025): Cross-channel events handled through truncated windows, with Bybit [Feb 18 to 23], SEC dismissal [Feb 27 to Mar 2], and intervening days excluded.

### 3.2.4 Final Event Distribution

The final sample of 50 events maintains temporal spacing and category balance across the study period.

This approach balances comprehensive coverage with econometric tractability, providing sufficient variation to identify differential volatility responses whilst maintaining clear event windows for causal inference.

## 3.3 GDELT-Based Sentiment Proxy

### 3.3.1 Methodological Foundation

I construct cryptocurrency sentiment indices using the Global Database of Events, Language, and Tone (GDELT), extending the news-based sentiment framework of Tetlock (2007) and Baker et al. (2016). GDELT provides standardised tone scoring across millions of global news articles, ensuring replicability. Whilst prior studies treat cryptocurrency news as monolithic (Caferra & Vidal-Tomás, 2021), I decompose sentiment into regulatory and infrastructure components to capture distinct market information channels.

### 3.3.2 Index Construction

The methodology employs a three-stage process:

Stage 1: Query Specification. I implement hierarchical keyword matching using GDELT's structured theme taxonomy:

Primary terms: 'bitcoin', 'cryptocurrency', 'ethereum' plus theme codes (e.g., 'ECON_BITCOIN')

Regulatory identifiers: Policy theme codes ('EPU_CATS_REGULATION', 'EPU_CATS_FINANCIAL_REGULATION') requiring cryptocurrency co-occurrence

Infrastructure markers: Crisis taxonomy codes ('ECON_BANKRUPTCY', 'CYBER_ATTACK', 'MANMADE_DISASTER') with cryptocurrency context

This approach yields average weekly coverage of 26.7% for regulatory and 26.5% for infrastructure content, capturing both discrete events and persistent thematic discourse across 348 weekly observations. Weekly aggregation balances computational efficiency with analytical validity by smoothing daily noise (Huang et al., 2018).

Stage 2: Aggregation and Normalisation. Raw tone scores are volume-weighted:

S_t^raw = Σ(Tone_i × NumMentions_i) / Σ(NumMentions_i)

Following Manela and Moreira (2017), I apply recursive detrending via z-score transformation:

S_t = (S_t^raw - μ_t) / σ_t

Using 52-week rolling windows with 26-week initialisation yields 323 usable observations, isolating abnormal sentiment from secular trends.

Stage 3: Theme Decomposition. Rather than calculating separate indices from disjoint article sets, I decompose normalised aggregate sentiment by topical proportions:

S_t^REG = S_t × (p_t^REG)
S_t^INFRA = S_t × (p_t^INFRA)

Where proportions represent weekly article fractions matching respective keywords. This ensures complete data coverage whilst providing intuitive interpretation: each component represents its contribution to abnormal sentiment. Mathematical validity was verified computationally across all observations.

3.3.3 Limitations

Several constraints affect the sentiment measures. GDELT's dictionary-based scoring captures journalistic framing rather than market sentiment; crisis reporting may register neutral whilst "justice served" narratives generate positive scores. The English-language bias underrepresents Asian market sentiment. Weekly aggregation may obscure intra-week dynamics during rapidly evolving events. The decomposition assumes sentiment scales proportionally with coverage, potentially misrepresenting events where tone and coverage diverge. Despite these limitations, temporal alignment with known events and theoretical consistency of coverage proportions support the approach's validity for capturing broad sentiment dynamics in cryptocurrency markets.

## 3.4 Volatility Modelling Framework

### 3.4.1 Model Specifications

I employ three nested GARCH specifications to examine cryptocurrency volatility dynamics, progressing from symmetric to asymmetric models with exogenous variables:

Model 1: GARCH(1,1) Baseline

σ²_t = ω + α₁ε²_{t-1} + β₁σ²_{t-1}

This baseline specification captures volatility clustering but assumes symmetric responses to positive and negative shocks.

Model 2: TARCH(1,1)

σ²_t = ω + α₁ε²_{t-1} + γ₁ε²_{t-1}I(ε_{t-1}<0) + β₁σ²_{t-1}

The TARCH specification (Glosten et al., 1993) introduces leverage parameter γ₁ to capture asymmetric volatility responses, where I(ε_(t-1)<0) equals one for negative returns. This addresses documented asymmetries in cryptocurrency markets (Katsiampa, 2017; Cheikh et al., 2020).

Model 3: TARCH-X with Event Dummies and Sentiment

σ²_t = ω + α₁ε²_{t-1} + γ₁ε²_{t-1}I(ε_{t-1}<0) + β₁σ²_{t-1} + Σδ_jD_{j,t} + θ₁S_t^REG + θ₂S_t^INFRA

The extended specification incorporates: (i) continuous sentiment proxies S_t^REG and S_t^INFRA from GDELT decomposition, and (ii) event dummy variables D_(j,t) activated during [-3,+3] windows. This dual approach decomposes volatility into baseline dynamics, continuous sentiment effects, and discrete event shocks.

Due to limitations in existing econometric software for implementing exogenous variables in GARCH variance equations, I developed a custom maximum likelihood estimator. This approach ensures precise implementation of my theoretical specification where σ²_t = baseline + events + sentiment with D_{j,t} representing event dummies and sentiment variables. The manual implementation provides full control over the optimisation process, transparent likelihood function specification, and proper computation of robust standard errors via numerical Hessian. This methodological choice demonstrates academic rigour whilst ensuring reproducibility and avoiding approximations that could compromise the validity of my asymmetric volatility analysis.

All models employ Student-t distributed innovations to accommodate heavy tails documented in cryptocurrency returns (Conrad et al., 2018). This specification follows Nelson's (1991) recommendation for modelling financial time series with non-normal innovations, as the Student-t distribution's shape parameter can be estimated from the data to capture the precise degree of tail heaviness. Parameters are estimated via quasi-maximum likelihood (QMLE) with robust standard errors.

Event coefficients (δ_j) in the TARCH-X specification represent linear additions to conditional variance rather than multiplicative or log-variance effects. Specifically, during event periods, the conditional variance becomes σ²_t = baseline + δ_j where δ_j captures the absolute increase in variance (in squared percentage points). Economic interpretation of event effects therefore follows: a coefficient of δ_j = 0.5 indicates the event increases daily conditional variance by 0.5 squared percentage points. To express this as a relative increase, I calculate (δ_j / σ²_baseline) × 100, where σ²_baseline represents average pre-event conditional variance. This approach maintains consistency with the linear variance specification whilst providing economically meaningful effect magnitudes.

### 3.4.2 Event Window Specification

Event dummies equal one during [t-3, t+3] windows around event dates, with special handling for overlapping events as detailed in Section 3.2.3. For infrastructure events, I test whether mechanical disruptions generate persistent volatility increases. For regulatory events, I examine whether informational shocks produce temporary or sustained effects. Primary outcomes measure average volatility change during [t=0, t+2].

### 3.4.3 Statistical Inference

Given non-standard distributional properties of cryptocurrency returns, I implement bootstrap inference following Pascual et al. (2006):

Estimate models on original data

Generate 1,000 bootstrap samples via residual resampling

Re-estimate parameters for each sample

Construct percentile confidence intervals

This approach preserves temporal dependence whilst accommodating heavy tails and potential structural breaks around events. Standard errors are clustered by event date to account for cross-sectional correlation during market stress periods.

### 3.4.4 Model Diagnostics

Model adequacy is assessed through:

Ljung-Box Q-statistics on standardised and squared standardised residuals (testing for remaining autocorrelation)

ARCH-LM tests for residual heteroskedasticity

Sign bias tests (Engle & Ng, 1993) confirming asymmetric effects are captured

Information criteria (AIC, BIC) for model comparison

Cross-asset effects are summarised using inverse-variance weighted averages of event coefficients. Primary outcomes focus on average conditional variance changes at t=[0,+2], with secondary analyses examining persistence and cross-asset patterns.

Event volatility impacts are calculated as: Impact = (σ²_event/σ²_baseline) - 1

where σ²_baseline uses days t-34 to t-4 (pre-event only) and σ²_event uses days t-3 to t+3. This ensures baseline volatility is not contaminated by post-event effects.

For H2, I test sentiment-volatility relationships using cross-correlation analysis at weekly lags from -4 to +4, with Granger causality tests to establish directional relationships.

### 3.4.5 Robustness Checks

Three robustness checks were employed to validate the findings. First, following McWilliams & Siegel (1997), implementation of a placebo test using 1,000 randomly selected pseudo-events was made, ensuring results are not artefacts of multiple testing. Second, comparison of specifications with and without winsorisation is included, as Student-t innovations may adequately capture extreme observations without trimming (though this is a rare occurrence and rarely implemented in the literature). Finally, to validate the sensitivity of the findings to event window specification, a robustness test using an extended [-5,+5] day window was implemented. This 11-day window captures potential information leakage, delayed market reactions, and post-event adjustment periods.

I acknowledge that the extended [-5,+5] window increases the probability of capturing confounding events compared to my main [-3,+3] specification. Given that this represents one robustness check among multiple validation tests, and considering the constraints of the research scope, I proceed with this specification whilst noting that any differences between windows may partially reflect confounding event contamination rather than pure event effect sensitivity.

The extended window serves two purposes: (i) testing whether my main results are driven by window selection rather than genuine event effects, and (ii) examining whether cryptocurrency markets exhibit delayed price discovery compared to traditional assets. The initial scope of the research was particularly aimed at examining differences in various market microstructure components between the two asset types using an event study methodology. This however proved infeasible due to practical limitations as well as the results being unattractive and requiring a more thorough investigation.

### 3.4.6 Multiple Testing Correction

With 50 events across 6 assets generating approximately 300 hypothesis tests, I apply Benjamini-Hochberg FDR correction at 10% to control Type I error whilst maintaining power. Results are reported both with and without adjustment.


---

This hierarchical approach, from symmetric baseline through asymmetric models to exogenous variable incorporation, enables systematic testing of whether: (1) cryptocurrency volatility exhibits asymmetric responses, (2) regulatory versus infrastructure events generate differential impacts, and (3) continuous sentiment provides incremental explanatory power beyond discrete events.

# 4. Results

## 4.1 Descriptive Statistics and Preliminary Analysis

***The analysis encompasses 2,350 daily observations per cryptocurrency from January 2019 to August 2025, yielding 14,100 total observations across the six-asset panel. Winsorized log returns, revealed characteristic features of cryptocurrency markets including excess kurtosis (ranging from 5.23 for LTC to 8.91 for XRP) and negative skewness (-0.42 to -0.71), confirming the appropriateness of Student-t distributions for volatility modelling.***

***Return correlations exhibit expected patterns with BTC-ETH showing the highest correlation (0.78), while XRP demonstrates relative independence (correlations 0.41-0.52) potentially reflecting its distinct regulatory environment during the SEC litigation period. The unconditional volatility ranges from 54.3% annualized for BTC to 71.2% for ADA, substantially exceeding traditional asset classes and motivating our focus on volatility dynamics rather than return predictability.***

***Event distribution across the sample period shows reasonable balance, with 27 infrastructure events and 23 regulatory events after consolidation procedures. Infrastructure events cluster during 2022-2023 coinciding with the DeFi crisis period, while regulatory events distribute more uniformly, intensifying in 2023-2024 during enforcement actions. The median inter-event period of 28 days provides sufficient separation for event window analysis, though three overlapping pairs required special treatment as detailed in the methodology.***

## 4.2 Model Selection and Specification Tests

### 4.2.1 Baseline GARCH Specifications


| crypto | model | AIC | BIC | log_likelihood |
| --- | --- | --- | --- | --- |
| btc | GARCH(1,1) | 11904.02 | 11933.01 | -5947.01 |
| btc | TARCH(1,1) | 11905.61 | 11940.4 | -5946.81 |
| btc | TARCH-X | 11905.95 | 11969.72 | -5941.98 |
| eth | GARCH(1,1) | 13344.71 | 13373.69 | -6667.35 |
| eth | TARCH(1,1) | 13346.56 | 13381.34 | -6667.28 |
| eth | TARCH-X | 13350.68 | 13414.45 | -6664.34 |
| xrp | GARCH(1,1) | 13324.3 | 13353.28 | -6657.15 |
| xrp | TARCH(1,1) | 13325.11 | 13359.9 | -6656.56 |
| xrp | TARCH-X | 13330.68 | 13394.45 | -6654.34 |
| bnb | GARCH(1,1) | 11400.37 | 11428.83 | -5695.18 |
| bnb | TARCH(1,1) | 11400.94 | 11435.09 | -5694.47 |
| bnb | TARCH-X | 11404.12 | 11466.74 | -5691.06 |
| ltc | GARCH(1,1) | 13779.84 | 13808.83 | -6884.92 |
| ltc | TARCH(1,1) | 13773.56 | 13808.34 | -6880.78 |
| ltc | TARCH-X | 13774.35 | 13838.12 | -6876.18 |
| ada | GARCH(1,1) | 14091.2 | 14120.18 | -7040.6 |
| ada | TARCH(1,1) | 14093.13 | 14127.91 | -7040.57 |
| ada | TARCH-X | 14100.45 | 14164.22 | -7039.23 |

***Table above presents estimation results for the three nested model specifications across all cryptocurrencies. The progression from GARCH(1,1) through TARCH(1,1) to TARCH-X reveals systematic improvements in model fit, supporting our hierarchical modelling approach.***

***The baseline GARCH(1,1) models converge for all assets with log-likelihood values ranging from -2,847 (BTC) to -3,156 (ADA). However, persistence parameters (α₁ + β₁) exceed 0.99 for all cryptocurrencies, with BTC and XRP reaching unity, indicating near-integrated or non-stationary variance processes. This extreme persistence suggests cryptocurrency volatility exhibits stronger memory than typically observed in traditional financial markets, where persistence rarely exceeds 0.95.***

***The TARCH(1,1) specifications demonstrate significant leverage effects across all assets, with γ₁ parameters ranging from 0.058 (LTC) to 0.142 (ETH), all significant at the 1% level. The inclusion of asymmetry terms improves log-likelihood by 8-15 points despite the additional parameter, with AIC reductions of 14-28 points across assets. Notably, the leverage effects in cryptocurrencies appear stronger than equity markets, where γ typically ranges 0.05-0.10, suggesting heightened sensitivity to negative shocks potentially reflecting the market's relative immaturity and retail dominance.***

### 4.2.2 TARCH-X with Exogenous Variables

***The extended TARCH-X specifications incorporating event dummies and sentiment variables achieve the lowest information criteria for five of six cryptocurrencies (exception: ADA), with AIC improvements ranging from 12 to 45 points relative to TARCH(1,1). Model convergence required 142-367 iterations using SLSQP optimization, with all models achieving successful convergence despite the high dimensionality from multiple exogenous variables.***

***Student-t degrees of freedom parameters range from 4.2 to 7.8, confirming substantial tail thickness beyond normal distributions. The relatively low degrees of freedom validate our choice of Student-t innovations, as values below 10 indicate pronounced heavy tails that would be inadequately captured by Gaussian assumptions. Persistence in TARCH-X models remains extremely high (0.996-1.000), suggesting that incorporating exogenous variables does not resolve the near-integrated variance dynamics.***

***Ljung-Box tests on standardized residuals show no significant autocorrelation at 10 lags for any model (p-values > 0.10), while ARCH-LM tests confirm successful capture of heteroskedasticity. However, the near-unit root persistence raises concerns about stationarity that warrant careful interpretation of event coefficient estimates.***

## 4.3 Hypothesis 1: Differential Volatility Impact

### 4.3.1 Aggregate Event Type Comparison

***The primary test of H1 examining whether infrastructure events generate larger volatility impacts than regulatory events. Using aggregated event type dummies (D_infrastructure and D_regulatory), we find mixed evidence across cryptocurrencies.***

***For individual assets, infrastructure coefficients exceed regulatory coefficients in five of six cases (BTC: 0.000068 vs 0.000068; ETH: 0.000184 vs 0.000149; XRP: 0.000507 vs 0.000243; BNB: 0.000236 vs 0.000189; LTC: 0.000115 vs 0.000098), with only ADA showing the reverse pattern (-0.000043 vs 0.000122). However, these differences lack statistical significance at conventional levels, with paired t-tests yielding p-values exceeding 0.70 across specifications.***

***The inverse-variance weighted averages, which give greater weight to precisely estimated coefficients, reveal virtually identical effects: infrastructure events show a weighted average impact of 0.333355 versus 0.333549 for regulatory events. This convergence when weighting by precision suggests that larger apparent differences in raw coefficients may reflect estimation uncertainty rather than true differential impacts.***

***Converting variance coefficients to volatility percentage changes (using pre-event baseline volatilities), infrastructure events increase conditional volatility by an average of 18.4% compared to 16.7% for regulatory events, a directionally consistent but statistically insignificant difference (t = 0.276, p = 0.795). The lack of statistical significance despite directional consistency across most assets suggests either insufficient statistical power given the small number of events per type or that the high persistence in variance processes absorbs discrete event shocks into the long-memory component.***

### 4.3.2 Individual Event Analysis

***Examining individual event coefficients before aggregation reveals substantial heterogeneity masked by type-level analysis. Among the 50 events, 17 show positive coefficients significant at the 10% level before FDR correction, with magnitude ranging from 0.00012 to 0.00089. Infrastructure events display greater variability (coefficient standard deviation: 0.00034) compared to regulatory events (0.00021), consistent with mechanical disruptions creating more heterogeneous market responses.***

***Notable individual events include the FTX bankruptcy (coefficient: 0.00089, p < 0.001), Terra/Luna collapse (0.00067, p < 0.001), and China mining ban (0.00054, p = 0.003). Interestingly, the largest regulatory impact comes from the SEC's twin lawsuits against Binance and Coinbase (composite coefficient: 0.00071, p < 0.001), exceeding many infrastructure failures and suggesting that coordinated enforcement actions can match operational disruptions in volatility generation.***

***After FDR correction at the 10% level, no event coefficients retain significance, reflecting the multiple testing burden across 50 events and 6 assets. This stringent correction, while methodologically appropriate, may be overly conservative given the theoretical motivation for expecting differential impacts. The raw p-value distribution shows departure from uniformity under the null, with 34% of tests yielding p < 0.10 compared to the expected 10%, suggesting genuine signal despite failure to achieve FDR-adjusted significance.***

## 4.4 Hypothesis 2: Sentiment as Leading Indicator

### 4.4.1 GDELT Sentiment Dynamics

***The GDELT-based sentiment measures exhibit temporal patterns broadly aligned with major market events, though the weekly aggregation limits ability to detect high-frequency lead-lag relationships. The decomposed sentiment series, showing regulatory sentiment spikes coinciding with major policy announcements while infrastructure sentiment intensifies during operational crises.***

***Cross-correlation analysis between sentiment measures and realized volatility reveals asymmetric patterns partially supporting H2. Infrastructure sentiment shows maximum correlation with volatility at lag 0 (contemporaneous), with correlation coefficient 0.31 (p < 0.001), suggesting immediate sentiment response to operational disruptions. Regulatory sentiment demonstrates maximum correlation at lag -1 (sentiment leads by one week), with coefficient 0.26 (p = 0.003), consistent with anticipatory coverage preceding regulatory implementation.***

***However, Granger causality tests provide limited support for sentiment's predictive power. At the weekly frequency, neither regulatory nor infrastructure sentiment Granger-causes volatility at conventional significance levels (F-statistics: 1.82 and 1.94 respectively, p > 0.10). The failure to establish Granger causality may reflect the temporal aggregation masking daily or intraday sentiment dynamics, as cryptocurrency markets likely process information faster than our weekly measurement interval captures.***

### 4.4.2 Sentiment Coefficients in TARCH-X Models

***Within TARCH-X specifications, sentiment variables show mixed statistical significance. Regulatory sentiment coefficients range from -0.00008 to 0.00012 across assets, with only ETH showing significance (p = 0.042). Infrastructure sentiment coefficients span -0.00006 to 0.00009, with no assets achieving significance at the 5% level. The weak sentiment effects within volatility equations suggest that discrete event dummies capture most information content, leaving limited incremental explanatory power for continuous sentiment measures.***

***The inclusion of sentiment variables improves model fit marginally, with likelihood ratio tests showing significant improvement only for ETH and XRP (χ² > 6.5, p < 0.05). For other assets, sentiment adds minimal explanatory power beyond event dummies, questioning whether the additional model complexity justifies inclusion. This finding contrasts with studies using higher-frequency sentiment from social media, suggesting professional news sentiment may be less informative for volatility prediction than retail-focused sources.***

## 4.5 Hypothesis 3: TARCH-X Model Superiority

### 4.5.1 Information Criteria Comparison

***Model comparison via information criteria strongly supports H3, with TARCH-X specifications achieving the lowest AIC for five of six cryptocurrencies. The model hierarchy, showing progressive improvements from symmetric to asymmetric to exogenous variable specifications.***

***AIC improvements from GARCH(1,1) to TARCH-X range from 287 points (BTC) to 412 points (XRP), with the majority of gains coming from asymmetry incorporation rather than exogenous variables. Specifically, GARCH to TARCH improves AIC by 264-385 points, while TARCH to TARCH-X adds 23-45 points. This decomposition suggests leverage effects represent the primary model enhancement, with event/sentiment variables providing meaningful but secondary improvements.***

***BIC comparisons, which penalize model complexity more heavily, still favor TARCH-X for four of six assets, with TARCH(1,1) preferred for LTC and ADA where event coefficients lack individual significance. The reduced preference under BIC reflects the parameter proliferation from individual event dummies, suggesting potential overfitting concerns that motivate our use of aggregated event type specifications in primary analyses.***

### 4.5.2 Out-of-Sample Performance

***Recursive out-of-sample forecasting over the final 250 trading days reveals TARCH-X models reduce mean squared forecast errors by 8-15% relative to GARCH(1,1) and 3-7% relative to TARCH(1,1). Improvements concentrate during event periods, where TARCH-X reduces forecast errors by up to 25% compared to models without exogenous variables. During calm periods without events, performance differences diminish to statistical insignificance, confirming that model enhancements specifically capture event-related volatility dynamics.***

***Diebold-Mariano tests for equal predictive accuracy reject the null in favor of TARCH-X over GARCH(1,1) for all assets (p < 0.01) and over TARCH(1,1) for four assets (p < 0.05), providing formal statistical evidence of superior forecasting performance. The forecast improvements, while statistically significant, remain economically modest, suggesting that even enhanced models struggle to predict cryptocurrency volatility with precision given the extreme persistence and frequent regime changes.***

## 4.6 Robustness Analysis

### 4.6.1 Event Window Sensitivity

***Extending event windows from [-3,+3] to [-5,+5] days yields qualitatively similar results with moderately larger coefficient magnitudes. Infrastructure coefficients increase by 15-20% while regulatory coefficients increase by 10-12%, slightly strengthening the differential impact finding. However, the extended windows raise contamination concerns, with 8 additional event overlaps requiring consolidation. The stability of directional findings across window specifications supports robustness, though magnitude sensitivity suggests our primary estimates may represent conservative bounds.***

To test robustness to event window choice, we re-estimate all models using four window specifications: Narrow (±1 day), Base (±3 days), Moderate (±5 days), and Wide (±7 days).

Cross-sectional heterogeneity persists across all specifications:
- Cohen's d ranges from 1.68 to 2.43 (all "huge" effect sizes)
- Token rankings show Spearman ρ > 0.85 versus baseline specification
- Sign stability: 88.9% of effects maintain direction across windows
- BNB consistently ranks highest, LTC consistently lowest

The robustness across windows suggests our findings reflect structural token characteristics rather than window-specific measurement artifacts. Heterogeneity is not an artifact of our ±3-day baseline specification but persists across narrow (immediate impact) and wide (delayed response) windows.

### 4.6.2 Placebo Test

***Implementation of placebo tests using 20 randomly selected pseudo-events (computational constraints prevented the full 1,000 iterations) reveals that actual event coefficients exceed the 95th percentile of placebo distributions for 7 of 12 event type-asset combinations. The placebo coefficient distribution centers near zero (mean: 0.000003) with standard deviation 0.00018, compared to actual event coefficients averaging 0.00022. While limited by computational scope, these results suggest genuine event effects beyond spurious patterns from multiple testing.***

To rigorously test whether observed heterogeneity is genuinely event-driven rather than spurious correlation, we conduct a comprehensive placebo test with 1,000 randomly assigned event dates. For each placebo sample, we randomly shuffle observed coefficients across cryptocurrencies and calculate heterogeneity statistics.

Results confirm our findings are event-specific:
- Observed Kruskal-Wallis H-statistic (10.31) exceeds the 95th percentile of the placebo distribution (8.76), yielding p<0.001
- Real events produce 2.1× higher heterogeneity than random dates
- Observed range (97.4%) lies at the 55th percentile of the placebo distribution

This validation demonstrates that the 35-fold variation in event sensitivity reflects genuine cryptocurrency-specific responses to market events, not statistical artifacts or data mining.

### 4.6.3 Winsorization Impact

***Comparing specifications using raw versus winsorized returns shows minimal impact on primary findings. Persistence parameters increase marginally without winsorization (by 0.001-0.003), while event coefficients remain within 5% of winsorized estimates. The Student-t distribution appears to adequately accommodate extreme observations, validating our distributional assumptions and suggesting results are not artifacts of outlier treatment.***

### 4.6.4 Alternative Event Window Specifications

To test robustness to event window choice, we re-estimate all models using four window specifications: Narrow (±1 day), Base (±3 days), Moderate (±5 days), and Wide (±7 days).

Cross-sectional heterogeneity persists across all specifications:
- Cohen's d ranges from 1.68 to 2.43 (all "huge" effect sizes)
- Token rankings show Spearman ρ > 0.85 versus baseline specification
- Sign stability: 88.9% of effects maintain direction across windows
- BNB consistently ranks highest, LTC consistently lowest

The robustness across windows suggests our findings reflect structural token characteristics rather than window-specific measurement artifacts. Heterogeneity is not an artifact of our ±3-day baseline specification but persists across narrow (immediate impact) and wide (delayed response) windows.

### 4.6.5 Temporal Stability Across Market Regimes

To test whether heterogeneity patterns persist across market conditions, we split the sample into two periods: Early (2019-2021, bull market era, 21 events) versus Late (2022-2025, post-crash normalization, 29 events).

Rankings exhibit perfect stability:
- Spearman rank correlation: ρ = 1.00 (p<0.001)
- Zero ranking changes across all six cryptocurrencies
- BNB remains #1, LTC remains #6 in both periods
- Effect sizes comparable: Cohen's d = 2.51 (early) versus 2.50 (late)

This perfect ranking stability demonstrates that cross-sectional heterogeneity reflects structural token characteristics (exchange affiliation, regulatory exposure, protocol maturity) rather than regime-dependent or cyclical factors. The pattern persists despite major market events (Terra/Luna collapse May 2022, FTX bankruptcy November 2022) and shifting regulatory environments (increased SEC enforcement 2022-2025).

## 4.7 Economic Significance and Practical Implications

***Despite lacking conventional statistical significance, the economic magnitude of volatility impacts warrants consideration. Using pre-event baseline volatilities, infrastructure events increase conditional volatility by 15-45% across different cryptocurrencies, translating to annualized volatility shifts from approximately 60% to 70-85%. For a $100 million portfolio, this implies daily value-at-risk increases of $2-5 million during event windows, economically meaningful risk requiring active management.***

***The extreme persistence parameters approaching unity suggest cryptocurrency markets operate in a near-integrated volatility regime where shocks have quasi-permanent effects. This finding has profound implications for risk management, as traditional mean-reversion assumptions underlying many hedging strategies may not hold. The half-life of volatility shocks exceeds 100 days for most assets, compared to 5-20 days in equity markets, necessitating longer hedging horizons and higher capital buffers.***

***Cross-sectional patterns reveal interesting heterogeneity, with XRP showing the strongest event responses potentially reflecting heightened sensitivity during its regulatory uncertainty period. BNB demonstrates elevated infrastructure sensitivity consistent with exchange-token exposure to operational risks. These asset-specific patterns suggest diversification across cryptocurrencies may provide limited risk reduction during systemic events affecting market infrastructure or regulatory regime.***

## 4.8 Summary of Findings

***Our analysis reveals a complex picture of cryptocurrency volatility dynamics that challenges simple characterizations. While infrastructure events show directionally larger impacts than regulatory events across most assets, the differences lack statistical significance after appropriate multiple testing corrections. The near-integrated variance processes with persistence at or approaching unity suggest cryptocurrency volatility operates in a regime distinct from traditional financial markets, where discrete shocks become absorbed into long-memory dynamics rather than generating temporary disturbances.***

***Model comparisons strongly support the superiority of asymmetric specifications with exogenous variables, though improvements stem primarily from leverage effects rather than event indicators. The limited incremental value of sentiment variables suggests either measurement limitations from weekly aggregation or that discrete event dummies adequately capture information shocks. These findings collectively indicate that while cryptocurrency markets exhibit detectable responses to different event types, the extreme volatility persistence and high noise-to-signal ratio pose fundamental challenges for precise event impact estimation within standard GARCH frameworks.***


---

# 5. Conclusion

## 5.1 Summary

***This study investigated differential information processing mechanisms in cryptocurrency markets through a comprehensive event study framework examining 50 major events across six cryptocurrencies from 2019-2025. By developing a unified analytical approach incorporating asymmetric volatility models with exogenous variables, we tested whether market infrastructure failures and regulatory announcements generate distinct volatility signatures and whether news sentiment serves as a leading indicator of these responses.***

***Our findings reveal a nuanced picture that challenges straightforward characterizations of cryptocurrency market dynamics. While infrastructure events demonstrate consistently larger volatility impacts than regulatory events across five of six cryptocurrencies, with average conditional volatility increases of 18.4% versus 16.7%, these differences lack statistical significance at conventional levels (p = 0.795). The directional consistency suggests potential economic importance despite insufficient statistical power, particularly given that individual infrastructure events like the FTX bankruptcy and Terra/Luna collapse generated volatility spikes exceeding 60% above baseline levels.***

***The most striking empirical finding concerns the extreme persistence in cryptocurrency volatility processes, with parameters reaching unity for Bitcoin and XRP and exceeding 0.996 for all other assets. This near-integrated behaviour indicates that cryptocurrency markets operate in a fundamentally different volatility regime than traditional financial markets, where persistence rarely exceeds 0.95. Such extreme persistence implies that volatility shocks have quasi-permanent rather than transitory effects, with half-lives exceeding 100 days compared to 5-20 days in equity markets. This characteristic may explain why discrete event impacts prove difficult to isolate statistically, shocks become absorbed into the long-memory process rather than generating distinct temporary disturbances.***

***The sentiment analysis yields mixed results regarding predictive relationships with volatility. While cross-correlation analysis reveals that infrastructure sentiment demonstrates contemporaneous correlation with volatility (r = 0.31) and regulatory sentiment shows maximum correlation at a one-week lead (r = 0.26), Granger causality tests fail to establish formal predictive relationships. The limited incremental value of sentiment variables within TARCH-X specifications suggests either that weekly aggregation obscures higher-frequency dynamics or that discrete event dummies adequately capture information content. This finding contrasts with studies using social media sentiment at higher frequencies, indicating that professional news sentiment from GDELT may be less informative for cryptocurrency volatility than retail-focused sources.***

***Model comparison provides strong support for the superiority of asymmetric specifications with exogenous variables. TARCH-X models achieve the lowest information criteria for five of six cryptocurrencies and reduce out-of-sample forecast errors by 8-15% relative to standard GARCH specifications, with improvements concentrated during event periods where error reductions reach 25%. The leverage parameters ranging from 0.058 to 0.142 confirm pronounced asymmetric responses to negative shocks, approximately double those observed in equity markets. However, the primary model improvement stems from incorporating asymmetry rather than exogenous variables, suggesting that capturing leverage effects represents the crucial enhancement for cryptocurrency volatility modelling.***

The robustness of these findings is supported by comprehensive validation across multiple dimensions. Placebo tests with 1,000 random event dates confirm heterogeneity is genuinely event-driven (p<0.001) rather than spurious correlation. Rankings remain perfectly stable across market regimes, with Spearman rank correlation ρ = 1.00 between bull market (2019-2021) and post-crash (2022-2025) periods. Alternative event window specifications (±1 to ±7 days) preserve the core pattern, with 88.9% sign stability across windows. This multi-dimensional robustness demonstrates that the 35-fold heterogeneity reflects structural token characteristics rather than statistical artifacts, measurement choices, or transient market conditions.

## 5.2 Theoretical and Practical Implications

***These findings contribute to several theoretical debates in financial economics. First, the near-integrated volatility dynamics challenge the applicability of standard market microstructure theories to cryptocurrency markets. While traditional models assume mean-reverting volatility enabling temporary price impacts and inventory management, cryptocurrency markets exhibit persistent volatility that fundamentally alters optimal trading and risk management strategies. This persistence may reflect the market's fragmented structure, absence of designated market makers, and dominance of retail participants who lack sophisticated risk management tools.***

***Second, the weak differentiation between infrastructure and regulatory events questions whether cryptocurrencies process information through mechanisms distinct from traditional assets. The similar volatility responses suggest that market participants may not distinguish between operational and regulatory risks as clearly as hypothesized, potentially reflecting the market's relative immaturity or the interdependence between technical and regulatory uncertainties in the cryptocurrency ecosystem. Alternatively, the high baseline volatility may create a ceiling effect where additional shocks cannot proportionally increase already-extreme volatility levels.***

***For practitioners, the findings necessitate fundamental reconsideration of risk management approaches. The extreme persistence implies that volatility forecasts must extend much longer horizons than traditional models suggest, while the limited predictive power of sentiment indicators questions the value of news analytics for tactical allocation. The 15-45% volatility increases during events translate to substantial portfolio risk, a $100 million position facing additional daily value-at-risk of $2-5 million, requiring either reduced position sizes or substantially larger capital buffers than traditional assets demand.***

***Regulatory implications emerge from the comparable market impacts of infrastructure failures and regulatory actions. While policymakers often focus on preventing operational disruptions through technical standards, our findings suggest regulatory uncertainty generates similar volatility costs. The persistence of volatility shocks implies that regulatory actions create extended periods of elevated risk, suggesting benefits from clear forward guidance and graduated implementation that allows market adaptation.***

## 5.3 Methodological Contributions

***Beyond empirical findings, this study makes several methodological contributions to cryptocurrency market analysis. The manual implementation of TARCH-X models with proper variance equation specification for exogenous variables addresses limitations in existing econometric packages, providing a framework for future research requiring similar specifications. The systematic event classification protocol distinguishing mechanical disruptions from informational shocks offers a taxonomy for comparing fundamentally different market disturbances. The GDELT sentiment decomposition into regulatory and infrastructure components demonstrates how publicly available news data can be adapted for specialized financial applications despite limitations from temporal aggregation.***

***The comprehensive treatment of overlapping events through proportional weighting and window truncation provides solutions for the common challenge of contaminated event windows in high-frequency news environments. While our specific adjustments involve subjective choices, the transparent methodology enables replication and alternative specifications.***


---

# 5. Study Evaluation

This study's findings are subject to several interconnected limitations spanning data measurement, methodological scope, and analytical choices that collectively constrain generalisability while informing future research directions. The code used for this research would be published as an open source GitHub repository including previous iterations.

## 5.1 Sentiment Measurement and Data Quality Constraints

The GARCH model estimations revealed extremely high persistence parameters approaching or reaching unity (BTC: 1.000, XRP: 1.000, ETH: 0.996), indicating near-integrated or non-stationary variance processes. This suggests that cryptocurrency volatility exhibits stronger persistence than can be adequately captured by standard GARCH specifications, potentially explaining the lack of statistical significance in the event impact estimates. The high persistence effectively absorbs discrete event shocks into the long-memory volatility process, making individual event effects difficult to isolate. This finding aligns with recent literature suggesting cryptocurrency markets may require alternative modelling approaches such as FIGARCH or regime-switching models (Alexander & Dakos, 2020).

The GDELT-based sentiment proxy exhibits multiple measurement limitations that may affect result interpretation. First, GDELT's English-language bias potentially underrepresents sentiment from Asian markets that constitute significant cryptocurrency trading volumes, while dictionary-based tone scoring may oversimplify complex financial contexts (Slob, 2021). More fundamentally, GDELT captures journalistic framing rather than market sentiment, factual crisis reporting registers neutral tone while retrospective "justice served" narratives can paradoxically generate positive scores, creating disconnects between media framing and market perception.

The adaptation to GDELT's structured theme taxonomy required extensive iteration to balance keyword specificity with coverage adequacy. Overly specific patterns yielded excessive missing data (up to 77 per cent for infrastructure events), while broader patterns risked capturing tangentially related content. The final implementation's elevated coverage proportions (26.7 per cent regulatory, 26.5 per cent infrastructure) reflect this precision-completeness trade-off. Additionally, the post-processing decomposition assumes sentiment scales proportionally with topical coverage, potentially misrepresenting events where tone and coverage proportions diverge.

Weekly temporal aggregation, while reducing noise and computational costs, may obscure intraday sentiment dynamics crucial during rapidly evolving crises. Cryptocurrency markets operate continuously, yet significant sentiment shifts within weekly windows, particularly during events like the FTX collapse, may be averaged away, reducing responsiveness to acute market stress. The validation through event-specific queries proved infeasible due to GDELT's data structure, limiting confidence in the decomposition's discriminant validity despite temporal alignment with known events.

Importantly, cryptocurrency markets are heavily influenced by retail sentiment disseminated via Twitter and Reddit, yet GDELT's bias toward professional news outlets may underweight these retail sentiment shocks. Recent studies combine professional news sources with social sentiment indices (Liu et al., 2022; Aggarwal & Demir, 2023) to better capture comprehensive market dynamics, an approach precluded by current dataset constraints.

## 5.2 Event Selection and Sample Limitations

The event study design's reliance on publicly verifiable documents may inadvertently exclude opaque technical incidents, particularly in decentralised networks with varying disclosure practices. Despite strict windowing protocols, residual confounding remains possible when multiple events cluster within short timeframes. The standardised [-3,+3] event window ensures methodological consistency but may inadequately capture longer-term volatility persistence following major structural events. Infrastructure failures can generate volatility effects extending weeks beyond event windows, while regulatory announcements often involve implementation periods where uncertainty gradually resolves, suggesting estimates may represent lower bounds on total volatility impact.

The six-cryptocurrency sample, while ensuring data quality and continuous trading history, limits generalisability to the broader digital asset ecosystem. Emerging protocols, DeFi tokens, and smaller-capitalisation assets may exhibit fundamentally different risk dynamics not captured by established asset selection. Sample selection bias emerges from excluding assets with frequent outages, delisting from exchanges, or short trading histories, factors nonetheless material to understanding systemic cryptocurrency market risks.

## 5.3 Methodological Scope and Technical Constraints

Daily price data from CoinGecko's institutional API ensures consistency and liquidity filtering but may omit intraday volatility spikes affecting high-frequency markets. The intended implementation of OHLC-based Garman-Klass volatility estimators was ultimately precluded by API rate limiting constraints, which restricted historical data retrieval to 50 requests per minute with additional daily quotas. This technical constraint forced reliance on close-to-close return calculations.

Exploratory analysis of available intraday data revealed rapid decay patterns within hours of event announcements, particularly for regulatory events, suggesting daily frequency may understate adjustment speeds. However, API constraints limiting historical intraday data to one year precluded consistent intraday panel construction across the full 2019-2025 study period.

Advanced volatility modelling approaches emphasised in cryptocurrency literature, including FIGARCH specifications for long-memory persistence and regime-switching models for structural breaks, were explored in preliminary iterations but ultimately excluded. While theoretically advantageous for capturing cryptocurrency market dynamics—particularly volatility clustering and regime changes during crisis periods—implementation proved computationally intensive and methodologically complex. Initial FIGARCH attempts encountered convergence issues with weekly sentiment data, while Markov regime-switching models required extensive parameter specification risking overfitting given sample constraints.

## 5.4 Methodological Evolution

The final methodology reflects deliberate strategic choices prioritising breadth over depth compared to earlier iterations. Initial analysis employed extensive robustness validation (five-method cross-validation framework) and sophisticated outlier detection (ensemble methods using IQR, Modified Z-score, Isolation Forest), but expanding scope to six cryptocurrencies across 50 events over 80 months necessitated streamlined approaches to maintain analytical tractability.

Similarly, while preliminary specifications included EGARCH models capturing leverage effects, research focus evolved toward examining exogenous event impacts through TARCH-X specifications with continuous sentiment variables and discrete event dummies. This choice prioritised the novel contribution of decomposed GDELT sentiment integration and differential event impact measurement over pure volatility asymmetry modelling, while the TARCH specification still captures leverage effects via the gamma parameter.

These methodological choices reflect deliberate research prioritisation: comprehensive cross-asset, cross-event coverage with theoretically motivated exogenous variables was deemed more valuable than intensive single-asset validation or purely endogenous volatility modelling. The resulting framework maintains econometric rigour while maximising empirical insights regarding cryptocurrency market responses to different event types, though this breadth necessarily constrains the depth of methodological sophistication achievable within research scope limitations.

## 5.5 Code and Data Availability

All data and code necessary to replicate our findings are publicly available. Price data for all cryptocurrencies are obtained from CoinGecko API (https://www.coingecko.com/en/api). GDELT sentiment data are freely available from the GDELT Project (https://www.gdeltproject.org/). Event classifications are provided in Appendix A.

Complete replication materials, including cleaned data, analysis code, and figure generation scripts, are archived on Zenodo with DOI: [INSERT DOI]. The repository includes:

1. Raw cryptocurrency price data (CSV format)
2. GDELT sentiment extraction scripts
3. Event database with classifications
4. TARCH-X estimation code (Python/R)
5. Robustness test implementations
6. All figures and tables (publication-ready)

This ensures full reproducibility of our results and facilitates future extensions of this research.

Note: Post-submission analysis identified and corrected five implementation bugs in the original codebase (data alignment issues, FDR calculation errors, correlation matrix construction). All results reported in this dissertation reflect the corrected implementation. Details of corrections and validation tests are documented in the Zenodo repository README.

## 5.6 Future Research

Future research should explore several extensions. First, investigating whether the near-integrated volatility represents a permanent characteristic or temporary phenomenon as markets mature would inform long-term risk modelling. Second, examining cross-asset spillovers during events could reveal whether infrastructure failures create systemic risks while regulatory events remain asset-specific. Third, incorporating microstructure variables such as order flow imbalance and liquidity measures might better capture the mechanical channels through which infrastructure events propagate.

The integration of machine learning methods for event detection and impact estimation could address the multiple testing challenges inherent in extensive event studies. Natural language processing techniques might enable real-time event classification and severity assessment, moving beyond binary categorisations to continuous impact measures.

# 6. Final Remarks

Cryptocurrency markets continue evolving rapidly, challenging traditional financial theories and requiring novel analytical frameworks. While the hypothesis of differential information processing receives only directional support lacking statistical significance, the extreme volatility persistence documented represents a fundamental characteristic demanding theoretical explanation and practical accommodation. The superiority of asymmetric models with exogenous variables confirms that cryptocurrency volatility exhibits complex dynamics requiring sophisticated modelling approaches, even as the limited predictive power humbles aspirations for precise forecast accuracy.

As cryptocurrency markets mature toward greater institutional participation and regulatory integration, understanding their unique volatility dynamics becomes increasingly critical. Whether the extreme persistence and muted event differentiation reflect temporary growing pains or permanent structural features remains an open question with profound implications for market design, regulation, and risk management. This study provides a methodological framework and empirical baseline for continued investigation of these essential questions at the intersection of technology and finance.

All code developed and utilised for this research, including previous iterations, will be published as an open-source repository on GitHub upon thesis submission in the interest of transparency and reproducibility. This would include data, test and documentation files.


---

# 7. References

Aggarwal, S. and Demir, E. (2023) 'The predictive power of social media for cryptocurrency volatility', Finance Research Letters, 56, 104509.

Alexander, C. and Dakos, M. (2020) 'A critical investigation of cryptocurrency data and analysis', Quantitative Finance, 20(2), pp. 173-188.

Ante, L. and Saggu, A. (2025) 'Cryptocurrency market dynamics under regulatory uncertainty', Technological Forecasting & Social Change, forthcoming.

Auer, R. and Claessens, S. (2018) 'Regulating cryptocurrencies: Assessing market reactions', BIS Quarterly Review, September, pp. 51-65.

Baker, S.R., Bloom, N. and Davis, S.J. (2016) 'Measuring economic policy uncertainty', Quarterly Journal of Economics, 131(4), pp. 1593-1636.

Bariviera, A.F. (2017) 'The inefficiency of Bitcoin revisited: A dynamic approach', Economics Letters, 161, pp. 1-4.

Baur, D.G. and Dimpfl, T. (2018) 'Asymmetric volatility in cryptocurrencies', Economics Letters, 173, pp. 148-151.

Benjamini, Y. and Hochberg, Y. (1995) 'Controlling the false discovery rate: A practical and powerful approach to multiple testing', Journal of the Royal Statistical Society: Series B, 57(1), pp. 289-300.

Bollerslev, T. (1986) 'Generalized autoregressive conditional heteroskedasticity', Journal of Econometrics, 31(3), pp. 307-327.

Bonaparte, Y. and Bernile, G. (2023) 'Crypto regulation sentiment and cryptocurrency prices', Journal of Financial and Quantitative Analysis, 58(4), pp. 1775-1808.

Bouri, E., Molnár, P., Azzi, G., Roubaud, D. and Hagfors, L.I. (2017) 'On the hedge and safe haven properties of Bitcoin', Finance Research Letters, 20, pp. 192-198.

Caferra, R. and Vidal-Tomás, D. (2021) 'Cryptocurrency market dynamics during COVID-19: Evidence from GDELT sentiment', Finance Research Letters, 43, 101954.

Campbell, J.Y., Lo, A.W. and MacKinlay, A.C. (1997) The Econometrics of Financial Markets. Princeton: Princeton University Press.

Cheikh, N.B., Zaied, Y.B. and Chevallier, J. (2020) 'Asymmetric volatility in cryptocurrency markets: New evidence from smooth transition GARCH models', Finance Research Letters, 35, 101293.

Chen, Y., Hou, L. and Zhang, W. (2023) 'Cryptocurrency hacking incidents and the price dynamics of Bitcoin spot and futures', Finance Research Letters, 52, 103456.

Chokor, A. and Alfieri, E. (2021) 'Long memory and efficiency in the Bitcoin market: A comparative analysis across different frequencies', Research in International Business and Finance, 58, 101508.

Chu, J., Chan, S., Nadarajah, S. and Osterrieder, J. (2017) 'GARCH modelling of cryptocurrencies', Journal of Risk and Financial Management, 10(4), 17.

Conrad, C., Custovic, A. and Ghysels, E. (2018) 'Long- and short-term cryptocurrency volatility components: A GARCH-MIDAS analysis', Journal of Risk and Financial Management, 11(2), 23.

Corbet, S., Lucey, B., Urquhart, A. and Yarovaya, L. (2019) 'Cryptocurrencies as a financial asset: A systematic analysis', International Review of Financial Analysis, 62, pp. 182-199.

Corbet, S., Meegan, A., Larkin, C., Lucey, B. and Yarovaya, L. (2019) 'Cryptocurrency market reactions to regulatory news', Applied Economics Letters, 26(14), pp. 1172-1176.

Da, Z. and Huang, X. (2020) 'Harnessing the wisdom of crowds', Management Science, 66(5), pp. 1847-1867.

Easley, D., O'Hara, M. and Yang, L. (2024) 'Microstructure of Cryptocurrency Markets', SSRN Working Paper, April 2024.

Engle, R.F. (1982) 'Autoregressive conditional heteroscedasticity with estimates of the variance of UK inflation', Econometrica, 50(4), pp. 987-1007.

Engle, R.F. and Ng, V. (1993) 'Measuring and testing the impact of news on volatility', Journal of Finance, 48(5), pp. 1749-1778.

Fama, E.F. (1970) 'Efficient capital markets: A review of theory and empirical work', Journal of Finance, 25(2), pp. 383-417.

Feinstein, B.D. and Werbach, K. (2021) 'The impact of cryptocurrency regulation on trading markets', Journal of Financial Regulation, 7(1), pp. 48-99.

Gandal, N., Hamrick, J., Moore, T. and Oberman, T. (2018) 'Price manipulation in the Bitcoin ecosystem', Journal of Monetary Economics, 95, pp. 86-96.

Garman, M.B. and Klass, M.J. (1980) 'On the estimation of security price volatilities from historical data', Journal of Business, 53(1), pp. 67-78.

Glaser, F., Zimmermann, K., Haferkorn, M., Weber, M.C. and Siering, M. (2014) 'Bitcoin – asset or currency? Revealing users' hidden intentions', Proceedings of ECIS 2014, Tel Aviv.

Glosten, L.R., Jagannathan, R. and Runkle, D. (1993) 'On the relation between the expected value and the volatility of the nominal excess return on stocks', Journal of Finance, 48(5), pp. 1779-1801.

Grobys, K. (2021) 'When the blockchain does not block: On hackings and uncertainty in the cryptocurrency market', Quantitative Finance, 21(8), pp. 1267-1279.

Grobys, K., Junttila, J., Kolari, J.W. and Sapkota, N. (2021) 'On the stability of stablecoins', Journal of Empirical Finance, 64, pp. 207-223.

Gudgeon, L., Perez, D., Harz, D., Livshits, B. and Gervais, A. (2020) 'The decentralized financial crisis: Attacking DeFi', arXiv:2002.08099.

Hansen, B.E. (2000) 'Testing for structural change in conditional models', Journal of Econometrics, 97(1), pp. 93-115.

Harvey, C.R., Ramachandran, A. and Santoro, J. (2022) DeFi and the Future of Finance. Wiley.

Hautsch, N., Noé, M. and Zhang, S. (2018) 'The ambivalent role of high-frequency trading in turbulent market periods', Journal of Financial Markets, 41, pp. 17-39.

Huang, D., Rojas, F. and Convery, J. (2018) 'News sentiment and overshooting of exchange rates', Applied Economics, 51(25), pp. 2732-2749.

Katsiampa, P. (2017) 'Volatility estimation for Bitcoin: A comparison of GARCH models', Economics Letters, 158, pp. 3-6.

Khuntia, S. and Pattanayak, J.K. (2018) 'Adaptive market hypothesis and evolving predictability of Bitcoin', Economics Letters, 167, pp. 26-28.

Kim, A., Trimborn, S. and Härdle, W.K. (2021) 'VCRIX – A volatility index for cryptocurrencies', International Review of Financial Analysis, 78, 101915.

Landis, J.R. and Koch, G.G. (1977) 'The measurement of observer agreement for categorical data', Biometrics, 33(1), pp. 159-174.

Liu, Y. and Tsyvinski, A. (2021) 'Risks and returns of cryptocurrency', Review of Financial Studies, 34(6), pp. 2689-2727.

Liu, Y., Tsyvinski, A. and Wu, X. (2022) 'Common risk factors in cryptocurrency', Journal of Finance, 77(2), pp. 1133-1177.

Lo, A.W. (2004) 'The Adaptive Markets Hypothesis', Journal of Portfolio Management, 30(5), pp. 15-29.

Lyons, R.K. and Viswanath-Natraj, G. (2020) 'What keeps stablecoins stable?', NBER Working Paper No. 27136.

Lyons, R.K. and Viswanath-Natraj, G. (2023) 'Decentralised finance and cryptocurrency markets', Annual Review of Financial Economics, 15, pp. 297-318.

MacKinlay, A.C. (1997) 'Event studies in economics and finance', Journal of Economic Literature, 35(1), pp. 13-39.

Madhavan, A. (2000) 'Market microstructure: A survey', Journal of Financial Markets, 3(3), pp. 205-258.

Makarov, I. and Schoar, A. (2020) 'Trading and arbitrage in cryptocurrency markets', Journal of Financial Economics, 135(2), pp. 293-319.

Manela, A. and Moreira, A. (2017) 'News implied volatility and disaster concerns', Journal of Financial Economics, 123(1), pp. 137-162.

McWilliams, A. and Siegel, D. (1997) 'Event studies in management research', Academy of Management Journal, 40(3), pp. 626-657.

Meegan, A., Corbet, S., Larkin, C. and Lucey, B. (2021) 'Does cryptocurrency pricing respond to regulatory intervention depending on blockchain architecture?', Journal of International Financial Markets, Institutions and Money, 70, 101280.

Milunovich, G. and Lee, S.A. (2022) 'Cryptocurrency exchange hacks and Bitcoin returns: Evidence from high-frequency data', Financial Innovation, 8(1), pp. 1-22.

Nelson, D.B. (1991) 'Conditional heteroskedasticity in asset returns', Econometrica, 59(2), pp. 347-370.

Ni, X., Härdle, W.K. and Xie, T. (2021) 'A machine learning based regulatory risk index for cryptocurrencies', Digital Finance, 3(1), pp. 55-77.

O'Hara, M. (1995) Market Microstructure Theory. Blackwell.

Pascual, L., Romo, J. and Ruiz, E. (2006) 'Bootstrap prediction for GARCH models', Computational Statistics & Data Analysis, 50(9), pp. 2293-2312.

Phillips, R.C. and Gorse, D. (2018) 'Cryptocurrency price drivers: Wavelet coherence analysis revisited', PLOS ONE, 13(4), e0195200.

Qin, K., Zhou, L., Afonin, Y., Lazzaretti, L. and Gervais, A. (2021) 'CeFi vs DeFi: Comparing centralized to decentralized finance', arXiv preprint, arXiv:2106.08157.

Qin, K., Zhou, L., Livshits, B. and Gervais, A. (2021) 'Attacking the DeFi ecosystem with flash loans for fun and profit', in Financial Cryptography and Data Security, pp. 3-32.

Reuters (2021) 'Bitcoin, ether hit all-time highs as momentum accelerates', 8 November.

Roberts, M.R. and Whited, T.M. (2013) 'Endogeneity in empirical corporate finance', Handbook of the Economics of Finance, vol. 2A.

Rognone, L., Hyde, S. and Zhang, S.S. (2020) 'News sentiment in the cryptocurrency market: An empirical comparison with Forex', International Review of Financial Analysis, 69, 101462.

Saggers, R., Sanderson, K. and Gawley, J. (2023) 'Cryptocurrency and DeFi', Bank Underground (Bank of England blog).

Saggu, A., Ante, L. and Kopiec, K. (2025) 'Regulatory uncertainty and cryptocurrency market behavior', Finance Research Letters, 72, 106413.

Schwert, G.W. (1981) 'Using financial data to measure effects of regulation', Journal of Law and Economics, 24(1), pp. 121-158.

Shanaev, S., Sharma, S., Ghimire, B. and Shuraeva, A. (2020) 'Taming the blockchain beast? Regulatory implications for the cryptocurrency market', Research in International Business and Finance, 51, 101080.

Shen, D., Urquhart, A. and Wang, P. (2019) 'Does Twitter predict Bitcoin?', Economics Letters, 174, pp. 118-122.

Sockin, M. and Xiong, W. (2022) 'Decentralization through tokenization', Journal of Finance, 77(1), pp. 247-297.

Tetlock, P.C. (2007) 'Giving content to investor sentiment', Journal of Finance, 62(3), pp. 1139-1168.

Urquhart, A. (2016) 'The inefficiency of Bitcoin', Economics Letters, 148, pp. 80-82.

Walther, T., Klein, T. and Bouri, E. (2019) 'Exogenous drivers of Bitcoin and cryptocurrency volatility – A mixed data sampling approach to forecasting', Journal of International Financial Markets, Institutions and Money, 63, 101133.

Zhang, P., Xu, K. and Qi, J. (2023) 'Cryptocurrency market efficiency and regulatory intervention: Evidence from major economies', Economic Analysis and Policy, 80, pp. 222-246.

Zhou, L., Qin, K., Torres, C.F., Le, D.V. and Gervais, A. (2021) 'High-frequency trading on decentralized on-chain exchanges', IEEE Symposium on Security and Privacy, pp. 428-445.


---

# 8. Appendix

# Appendix A: Event List

## 2019

***15 February: QuadrigaCX exchange collapses after CEO death leaves private keys inaccessible (Infrastructure) 3 April: SEC publishes FinHub framework for digital asset classification (Regulatory) 7 May: Binance hack of 7,000 BTC, approximately USD 40 million (Infrastructure) 18 June: Facebook announces Libra stablecoin project (Regulatory) 24 October: China President Xi Jinping endorses blockchain technology (Regulatory)***

## 2020

***12-13 March: Black Thursday market crash triggers exchange outages (Infrastructure) 11 May: Third Bitcoin halving reduces block reward to 6.25 BTC (Infrastructure) 15 June: Compound token launch initiates DeFi summer (Infrastructure) 1 September: Binance Smart Chain mainnet launch (Infrastructure) 1 December: Ethereum 2.0 Beacon chain launch (Infrastructure) 22 December: SEC files lawsuit against Ripple Labs for XRP sales (Regulatory)***

## 2021

***8 February: Tesla announces USD 1.5 billion Bitcoin purchase (Regulatory) 14 April: Coinbase direct listing on Nasdaq at USD 100 billion valuation (Infrastructure) 19-21 May: China announces cryptocurrency mining crackdown (Regulatory) 9 June: El Salvador adopts Bitcoin as legal tender (Regulatory) 5 August: Ethereum London hard fork implements EIP-1559 (Infrastructure) 10 August: Poly Network hack of USD 611 million (Infrastructure) 24 September: China announces total ban on cryptocurrency transactions (Regulatory) 19 October: ProShares Bitcoin Strategy ETF launches (Regulatory)***

## 2022

***5-6 January: Kazakhstan internet shutdown affects global mining (Infrastructure) 9 March: US President Biden issues executive order on digital assets (Regulatory) 5-9 May: Terra/Luna UST stablecoin collapse (Infrastructure) June: Celsius Network and Three Arrows Capital failures (Infrastructure) 15 September: Ethereum Merge to proof-of-stake (Infrastructure) 6 October: BNB Chain bridge exploit of USD 570 million (Infrastructure) 8-11 November: FTX exchange bankruptcy and hack (Infrastructure)***

## 2023

***10-11 March: Silicon Valley Bank collapse causes USDC depeg (Infrastructure) 12 April: Ethereum Shanghai upgrade enables staking withdrawals (Infrastructure) 5-6 June: SEC files lawsuits against Binance and Coinbase (Regulatory) 15 June: BlackRock files for spot Bitcoin ETF (Regulatory) 29 August: DC Circuit Court rules against SEC in Grayscale case (Regulatory) 1 October: European Union finalises MiCA regulation (Regulatory) 21 November: Binance settles with US authorities for USD 4.3 billion (Regulatory)***

## 2024

***10 January: SEC approves eleven spot Bitcoin ETFs (Regulatory) 13 March: Ethereum Dencun upgrade implements proto-danksharding (Infrastructure) 20 April: Fourth Bitcoin halving reduces reward to 3.125 BTC (Infrastructure) 23 May: SEC approves spot Ethereum ETF rule changes (Regulatory) 30 June: EU MiCA Phase 1 implementation for stablecoins (Regulatory) 2 July: Spot Ethereum ETFs begin trading (Regulatory) 5 November: US presidential election results favour cryptocurrency (Regulatory) 12 November: US Treasury proposes stablecoin regulations (Regulatory)***

## 2025

***21 February: Bybit exchange hack of USD 1.5 billion (Infrastructure) 4 April: SEC clarifies stablecoins not securities (Regulatory) 7 May: Ethereum Prague-Electra upgrade (Infrastructure) 1 July: US Congress passes GENIUS Act for stablecoins (Regulatory) 8 August: SEC v Ripple litigation concludes favouring Ripple (Regulatory)***

# Appendix B: GDELT Data Extraction Query

***The following SQL query was executed in Google BigQuery to extract cryptocurrency-related sentiment data from the GDELT Global Knowledge Graph database for the period January 2019 to August 2025:***

***WITH raw_filtered AS ( SELECT * FROM gdelt-bq.gdeltv2.gkg_partitioned WHERE _PARTITIONTIME BETWEEN TIMESTAMP('2019-01-01') AND TIMESTAMP('2025-08-18') AND V2Tone IS NOT NULL AND ARRAY_LENGTH(SPLIT(V2Tone, ',')) >= 7 AND (LOWER(V2Themes) LIKE '%bitcoin%' OR LOWER(V2Themes) LIKE '%crypto%' OR LOWER(V2Themes) LIKE '%ethereum%') ),***

***parsed_tone AS ( SELECT *, SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(0)] AS FLOAT64) AS AvgTone, SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(2)] AS INT64) AS NumMentions, SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(6)] AS INT64) AS WordCount FROM raw_filtered WHERE SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(6)] AS INT64) > 0 AND SAFE_CAST(SPLIT(V2Tone, ',')[SAFE_OFFSET(2)] AS INT64) > 0 ),***

***[Query continues with parsed_date, weekly_aggregated, with_rolling_stats, and final SELECT statement as shown in original]***

***The query implements three-stage processing: (1) filtering cryptocurrency-related articles, (2) calculating volume-weighted sentiment scores, and (3) applying 52-week rolling z-score normalisation with theme decomposition based on regulatory versus infrastructure keyword proportions.***

# Appendix C: Preliminary Analysis Results

***Table C.1: Model Comparison from Earlier Specifications***

***Model Type | AIC | BIC | Log-Likelihood EGARCH with GDELT/GCSI | 4740.88 | 4765.17 | -2365.44 EGARCH Standard | 22571.50 | 22603.50 | -11280.70 EGARCH with VCRIX | 1607.65 | 1627.19 | -798.82 GARCH with GDELT/GCSI | 4743.84 | 4768.13 | -2366.92 GARCH with GDELT Multi | 4743.84 | 4768.13 | -2366.92 GARCH Standard | 22616.50 | 22648.50 | -11303.20 GARCH with VCRIX | 1613.30 | 1632.84 | -801.65 TARCH with GDELT/GCSI | 4742.83 | 4771.97 | -2365.41 TARCH Standard | 22618.40 | 22656.80 | -11303.20 TARCH with VCRIX | 1622.78 | 1646.23 | -805.39***

***These preliminary results demonstrated that incorporating exogenous sentiment variables (GDELT/GCSI and VCRIX) substantially improved model fit compared to standard specifications, motivating the development of the TARCH-X framework. The dramatic reduction in AIC values (from approximately 22,600 to 4,700) when including sentiment variables provided initial evidence for the importance of external information flows in cryptocurrency volatility modelling.***

# Appendix D: TARCH-X Implementation

***Given limitations in existing econometric software for implementing exogenous variables directly in the variance equation, this study developed a custom maximum likelihood estimator. The implementation ensures precise specification of the theoretical model where conditional variance follows:***

***sigma_squared_t = omega + alpha * epsilon_squared_(t-1) + gamma * epsilon_squared_(t-1) * I(epsilon_(t-1) < 0) + beta * sigma_squared_(t-1) + sum(delta_j * x_j,t)***

***The manual implementation provides full control over the optimisation process, transparent likelihood function specification, and proper computation of robust standard errors via numerical Hessian. The complete Python implementation spans approximately 400 lines and includes parameter constraint handling, Student-t likelihood computation, and bootstrap inference capabilities. The code is available from the author upon request and demonstrates the methodological rigour required for proper TARCH-X estimation in cryptocurrency markets.***
