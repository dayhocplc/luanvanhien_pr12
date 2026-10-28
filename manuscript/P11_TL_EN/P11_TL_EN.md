---
title: "When a Screening Tool Is Trained on Rebalanced Data: Class-Imbalance Handling, the Risk Figure Told to Families, and the Waiting List of a Child Psychological Service — A Simulation Study"
---

**Authors:** [Author 1]^1,\*^, [Author 2]^1^, [Author 3]^2^

^1^ Faculty of Information Technology, Lac Hong University, Bien Hoa, Dong Nai, Viet Nam

^2^ [Affiliation — a child clinical psychologist co-author is recommended]

^\*^ Corresponding author: [e-mail]

**Running head:** REBALANCED SCREENING TOOLS IN PSYCHOLOGICAL SERVICES

# ABSTRACT

Digital developmental screening tools are often trained on "rebalanced" data — under-sampling, over-sampling, SMOTE or class weights — because affected children are a small minority. We asked what this technical choice does to the two things a child psychological service actually uses: the risk figure communicated to families and the list of children referred for specialist assessment. Using synthetic parent-report data generated from a 20-item questionnaire covering six developmental domains (8,554 positive and 123,150 negative records), a community prevalence of 2%, logistic regression and random forest, five training strategies, 20 replications and a fixed population of 50,000 children, we found that training after SMOTE raised the mean predicted risk of logistic regression to 0.415 (20.8 times the true rate) and placed 86.0% of children in a "20% or higher" band in which only 23 per 1,000 were affected; a "refer at 5% risk" rule then referred virtually every child. When the service admitted a fixed 5% of children with the highest scores, rebalancing did not help logistic regression and reduced the yield of random forest from 7.1 to 5.4 true cases per 100 assessments, with under-sampling the only exception. Two label-free repairs — analytical prior correction and "mean matching" to a known prevalence — almost fully restored logistic regression (expected calibration error 2.1–2.9 per 1,000) but not random forest after over-sampling, SMOTE or class weighting, whose risk scale was distorted in shape (calibration slope 0.29–0.42). Updating on 100–200 local labelled records was worse than mean matching to a known prevalence. We propose six questions a psychological service should ask a tool vendor and release an open-source audit tool. All findings come from synthetic data and require field validation.

**Keywords:** child clinical psychology; digital decision support; class imbalance; risk communication; service capacity.

**Public significance statement.** Screening apps are often built with data "rebalancing" tricks that make the risk numbers they display many times too high. In a simulation, this made most families hear an alarming risk figure and sent almost every screened child to the assessment waiting list, without finding more affected children. A simple check on the tool's output can detect and often repair the problem before the tool is used.

# 1. INTRODUCTION

## 1.1. Digital tools in the child psychological care pathway

Developmental screening is the entry point of a care pathway: a questionnaire is completed in the community or in primary care, children with concerning results are referred to a psychologist or a multidisciplinary team for specialist assessment, and only after that assessment is a diagnosis made and an intervention planned (Hyman et al., 2020). In Viet Nam, a national toolkit for the early detection of autism spectrum disorder has been issued by the Ministry of Health (Ministry of Health of Viet Nam, 2021), and digital applications increasingly score the questionnaires, store them and suggest referrals. In psychology, this sits within the broader movement towards measurement-based care and digital mental health (Lewis et al., 2019; Torous et al., 2021): tools do not replace clinicians but inform their decisions, and structured prediction has long been known to be at least as accurate as unaided judgement (Grove et al., 2000). A decision-support system is useful, however, only if its output is read as what it is (Sutton et al., 2020).

The output of a screening tool is used in two ways that demand two different qualities. The first is **talking to families**: a psychologist or health worker reads out a number or a risk band, and parents understand it as the probability that their child has a disorder. Communicating risk well is an evidence-based clinical skill (Zipkin et al., 2014; Spiegelhalter, 2017), and it is possible only if the number on the screen really is a probability — that is, if it is **calibrated** (Van Calster et al., 2019). The second is **ordering the waiting list**: a psychological service has limited assessment capacity, and the tool decides who is seen first. This mainly requires the tool to **rank** children correctly and — if referral is decided by a risk threshold — requires that threshold to mean what it says, so that the number of referrals matches what the service can absorb.

## 1.2. Class imbalance and the habit of rebalancing

About 1% of children in the community are autistic (Zeidan et al., 2022), and screen-positive rates of parent questionnaires are a few per cent (Robins et al., 2014; Aishworiya et al., 2023). Machine-learning texts call this **class imbalance**, and the common reflex is to rebalance the training set: under-sample the majority class, over-sample the minority class, create synthetic minority cases with SMOTE (Chawla et al., 2002), or give the minority class a larger weight (He & Garcia, 2009; Fernández et al., 2018). A recent field study of 3,639 Vietnamese toddlers screened with the Vietnamese M-CHAT-R reported a random forest trained with SMOTE that reached an AUC of 0.983 but a precision of only 0.351 at a prevalence of about 2% (Vo et al., 2026) — an illustration that an excellent ranking statistic can coexist with a substantial false-alarm rate.

Methodological work has shown that imbalance "corrections" damage probability calibration while rarely improving discrimination, both for logistic regression (van den Goorbergh et al., 2022) and for machine-learning models (Carriero et al., 2025). In theory, rebalancing is equivalent to changing the prior class probability and can be undone with Bayes' rule when the original prior is known (Elkan, 2001; Saerens et al., 2002; Dal Pozzolo et al., 2015). These results, however, are written in the language of statisticians — Brier scores, calibration slopes, AUC — not in the language of a psychological service: how many families will hear an inflated risk figure, how much longer the waiting list will be, and how many affected children will not be prioritised. When a hospital or an early-intervention centre buys or receives a tool, it usually has no control over how the tool was trained; it only sees the output. The practical question is therefore: **from the output alone, can a service recognise and repair the consequences of rebalancing?**

## 1.3. Aims

This simulation study answers three questions, set in a psychological service that receives children from community screening at a prevalence of 2%:

1. **The figure told to families.** How does rebalancing the training data change the share of children placed in each risk band, and is the band still truthful?
2. **The waiting list.** When the service admits children up to a fixed capacity, does rebalancing find more affected children? When it admits children above a risk threshold, how many are referred and how does the net benefit of the decision change?
3. **Checking and repairing before use.** When the vendor has rebalanced, can the service repair the risk scale with no — or few — local labelled records, and when is repair impossible?

A fuller grid (seven imbalance strategies × four models × four prevalences) is reported separately for a methodological audience ([Author], 2026a; [Author], 2026b); here we summarise that grid briefly (Section 3.1) and focus on three new analyses aimed at clinical users.

# 2. METHOD

The simulation is described following the ADEMP structure (aims, data-generating mechanisms, estimands, methods, performance measures) (Morris et al., 2019), and reporting follows the relevant items of TRIPOD+AI (Collins et al., 2024). **No data from real children were used**, so ethical approval was not required.

## 2.1. Synthetic data

Data were produced with the simulator of a hybrid rule-based/machine-learning screening system under development (Nguyen, 2026). The generator simulates parents' answers to a 20-item questionnaire covering six developmental domains (communication–language, gross motor, fine motor, imitation–learning, personal–social, atypical behaviour), including item non-response and response noise. Each record is summarised into six domain risk scores on a 0–1 scale by the system's fuzzy inference layer; these six scores are the model inputs. We generated a positive pool (14,000 records) and a negative pool (200,000 records) separately; after removing records with more than 30% missing items or a missing domain score, following the tool's own rejection rule, 8,554 and 123,150 records remained. Each pool was split once into a **development** half (for training: 4,277 positive, 61,575 negative) and a **deployment** half (for evaluation). Because the generator uses prevalence only when assigning the label, resampling the two pools at any rate reproduces the population distribution at that prevalence. The pools are identical to those of the companion study (SHA-256 fingerprint `ab3c60d495f1…`).

**Deployment population.** From the deployment half we drew, once, a population of 50,000 children with exactly 1,000 affected children (2%), playing the role of all children screened in one catchment area in one year. The remainder of the deployment half (3,277 positive, 12,575 negative) was used only to draw the **labelled audit samples** of Section 2.5, so no record was used both to repair the scale and to evaluate it.

## 2.2. Models and five training strategies

In each replication a training set of 5,000 records at 2% prevalence (100 affected children) was drawn from the development half. Two models common in the machine-learning screening literature were trained: **logistic regression** (L2 penalty, C = 1) and **random forest** (Breiman, 2001) (200 trees, at least five records per leaf). Each model was trained in five ways: (i) **as collected**; (ii) **under-sampling** — randomly discarding unaffected children until both classes were equal (100 + 100 records); (iii) **over-sampling** — randomly duplicating affected children until both classes were equal; (iv) **SMOTE** — generating synthetic affected children by interpolating towards one of their five nearest same-class neighbours (Chawla et al., 2002); (v) **class weights** — giving both classes equal total weight. The last four raise the effective share of the affected class in training to 50%.

## 2.3. Two ways of running a service

**Capacity-based.** The service can assess only K% of screened children (K = 2, 5 or 10%) and admits the K% with the highest scores. This uses only the **ranking** and is therefore independent of the risk scale. The outcome is the **number of true cases per 100 assessments** (positive predictive value at capacity K), together with sensitivity — the share of affected children who make the list. When several children share the score at the capacity boundary, we used the expectation of a random draw within the tie. The reference is assessing at random: two true cases per 100 assessments.

**Threshold-based.** A child is referred when the displayed risk is at least $p_t$, $p_t \in \{2, 5, 10\%\}$. The threshold encodes the trade-off the service accepts: $p_t = 5\%$ means accepting at most 19 assessments of unaffected children to find one affected child (Wynants et al., 2019). We report the share of children referred — a direct measure of the **load** on the waiting list — and the net benefit of decision curve analysis (Vickers & Elkin, 2006; Vickers et al., 2016):

$$\mathrm{NB}(p_t) = \frac{\mathrm{TP}}{n} - \frac{\mathrm{FP}}{n} \cdot \frac{p_t}{1 - p_t}, \qquad (1)$$

where TP and FP are the numbers of referred children with and without the disorder and $n$ the number screened. The two reference strategies are "refer none" (NB = 0) and "refer all" (NB = $\pi - (1-\pi)\,p_t/(1-p_t)$ with $\pi = 0.02$; exactly 0 at $p_t = 2\%$). A rule is useful at $p_t$ only if its net benefit exceeds both references.

## 2.4. The figure told to families

To mimic how results are discussed, risk was grouped into four bands — below 1%, 1–5%, 5–20% and 20% or higher — an illustrative convention of this study, not a clinical standard. For each training strategy we recorded the share of children in each band and the true rate of the disorder within the band, expressed as natural frequencies ("per 1,000 children"), which both professionals and families understand better than conditional probabilities (Gigerenzer & Hoffrage, 1995). A band is truthful if the number of affected children per 1,000 lies within the range its label promises.

## 2.5. Checking and repairing the scale before deployment

We assumed that the service receives a trained model and compared five ways of handling its output $p$. Let $\sigma(z) = 1/(1+e^{-z})$ and $\mathrm{logit}(p) = \ln[p/(1-p)]$.

(a) **Raw output** of the model.

(b) **Prior correction** (Elkan, 2001; Saerens et al., 2002). If the vendor discloses the original training prevalence $\pi$ and the prevalence after rebalancing $\pi_s$ (here 0.5), the probability is mapped back with Bayes' rule

$$p' = \frac{p\,\pi/\pi_s}{p\,\pi/\pi_s + (1-p)(1-\pi)/(1-\pi_s)}. \qquad (2)$$

Equation (2) is exact when rebalancing only shifts the prior and the model estimates the conditional probability correctly under $\pi_s$. It needs no labels but needs information that vendors rarely publish.

(c) **Mean matching** (no labels and no vendor information). The service runs the tool on its own population (without knowing who is affected) and chooses a log-odds shift $\delta$ so that the mean risk equals the prevalence $\hat\pi$ it estimates from epidemiological data:

$$\frac{1}{n}\sum_{i=1}^{n} \sigma\big(\mathrm{logit}(p_i) + \delta\big) = \hat\pi, \qquad p_i' = \sigma\big(\mathrm{logit}(p_i) + \delta\big). \qquad (3)$$

To measure the cost of a wrong prevalence estimate we used $\hat\pi$ = 2% (correct), 1% and 4% (wrong by a factor of two in either direction).

(d) **Intercept update** on $n$ local labelled records (Steyerberg et al., 2004; Janssen et al., 2008): as (3), but $\delta$ is chosen so that the summed risk equals the number of affected children observed in the sample — which is exactly the maximum-likelihood estimate of the intercept with the slope held fixed.

(e) **Platt refit** on the same $n$ records: logistic regression of the label on $\mathrm{logit}(p)$ (default L2 penalty), re-estimating both intercept and slope.

Labelled samples of $n \in \{100, 200, 500\}$ records were drawn from the reserved part of the deployment half, with a binomial number of affected children (mean 1.9, 3.4 and 9.7), as when a service takes $n$ consecutive records with a completed specialist assessment. Repairs (b)–(d) are strictly increasing transformations and **do not change the ranking**; capacity-based results are therefore independent of the repair.

## 2.6. Measures and statistical analysis

**Mean risk** versus the true prevalence measures calibration-in-the-large, the lowest level of the calibration hierarchy (Van Calster et al., 2016). The **expected calibration error** (ECE) splits the population into ten groups by quantiles of risk and averages, weighted by group size, the absolute difference between mean risk and observed rate. The **calibration slope** is the coefficient of $\mathrm{logit}(p)$ in an unpenalised logistic regression of the label on $\mathrm{logit}(p)$; 1 is ideal, and values below 1 mean the risks are **too extreme** (too high for high scorers and too low for low scorers) — a distortion of **shape** that no shift can repair. The **Brier score** (Brier, 1950) and the PR-AUC (area under the precision–recall curve) are used in the main grid.

All measures are means over 20 replications; each replication redraws the training set and the labelled samples, while the deployment population is fixed. For each model, every training strategy (and every repair) was compared with training as collected using paired per-replication differences and a one-sample t-test. The family of 108 comparisons (true cases per 100 assessments at three capacities; net benefit of the raw output, after prior correction and after mean matching at three thresholds) was adjusted with the Benjamini–Hochberg procedure at a false discovery rate of 0.05 (Benjamini & Hochberg, 1995); the family keeps six trivial comparisons (prior correction of the as-collected model is the identity), which makes the procedure slightly conservative. Random seeds are fixed and logged together with source-code fingerprints; re-running reproduces the result files byte for byte (Data and code availability).

## 2.7. Output-audit tool

From the results of Section 2.5 we wrote a command-line tool that depends only on numpy. Its input is a CSV file of the screening tool's scores for local children (with or without labels), the estimated prevalence and the service capacity. It reports: (1) the **inflation factor** — mean risk divided by prevalence, with a warning above 1.5; (2) the share of children referred at each threshold, compared with capacity; (3) the score cut-off matching capacity and the number of children tied at the boundary; (4) the scale after mean matching (or prior correction if the vendor disclosed the training prevalences) with a before–after table of risk bands; and (5) with labels, the observed rate with a 95% Wilson interval, the calibration slope (only with at least ten affected children) and net benefit before and after. The warning thresholds are conventions derived from the simulation, not clinical standards.

# 3. RESULTS

## 3.1. Main grid: rebalancing rarely helps discrimination and always damages probabilities

Table 1 summarises the main grid of the companion study at 2% prevalence (20 replications, a test set of 50,000 records per prevalence; 176 configurations and 256 Benjamini–Hochberg-adjusted tests). Across four prevalences and four models, the four rebalancing strategies worsened the Brier score significantly in 64/64 cells. PR-AUC improved significantly in only 12/64 cells — all involving fuzzy k-NN (a model with almost no discrimination on these data) or random forest with under-sampling, the largest gain being 13.2 per 1,000 — and deteriorated significantly in 36. Net benefit at the 2% threshold fell significantly in 32/64 cells and rose in 13, mostly for fuzzy k-NN and at 5% prevalence, where "refer all" is already a good strategy at a 2% threshold. Logistic regression and the hybrid model trained after rebalancing flagged almost every child at all four prevalences.

**Table 1.** *Main grid at 2% prevalence: PR-AUC, Brier score, share of children referred and net benefit under the rule "refer when risk ≥ 2%". Threshold moving uses exactly the as-collected model and only re-selects the cut-off on a 2,000-record calibration set, so its PR-AUC and Brier score equal those of the as-collected model by construction. Means over 20 replications. Reference values: the Brier score of a constant forecast of 0.02 is 19.6 per 1,000; the PR-AUC of a random forecast is 20 per 1,000.*

| Model | Training | PR-AUC ×1,000 | Brier ×1,000 | Children referred | Net benefit ×1,000 |
|:--------------------|:------------------|:----------:|:----------:|:----------:|:----------:|
| Logistic regression | As collected | 60.7 | 19.2 | 33.0% | 6.59 |
|  | Under-sampling | 56.3 | 215.2 | 100.0% | 0.00 |
|  | SMOTE | 59.7 | 205.4 | 100.0% | 0.00 |
|  | Threshold moving | 60.7 | 19.2 | 37.5% | 6.23 |
| Random forest | As collected | 48.3 | 19.6 | 31.0% | 5.56 |
|  | Under-sampling | 53.1 | 215.2 | 100.0% | 0.00 |
|  | SMOTE | 38.1 | 46.2 | 65.2% | 4.00 |
|  | Threshold moving | 48.3 | 19.6 | 33.7% | 5.17 |
| Fuzzy k-NN | As collected | 22.0 | 28.3 | 4.7% | 0.97 |
|  | Under-sampling | 28.4 | 293.5 | 72.8% | 2.59 |
|  | SMOTE | 23.9 | 77.8 | 12.8% | 1.86 |
|  | Threshold moving | 22.0 | 28.3 | 3.1% | 0.69 |
| Three-branch hybrid | As collected | 40.4 | 55.7 | 100.0% | 0.00 |
|  | Under-sampling | 40.4 | 172.9 | 100.0% | 0.00 |
|  | SMOTE | 38.1 | 102.8 | 100.0% | 0.00 |
|  | Threshold moving | 40.4 | 55.7 | 37.2% | 5.18 |

The rest of the Results focuses on logistic regression and random forest — the two models with real discrimination (AUC about 0.69–0.73) and the most common in practice.

## 3.2. The figure told to families

Rebalancing multiplied the mean risk of logistic regression by 22.1 (under-sampling), 21.0 (over-sampling), 20.8 (SMOTE) and 21.0 (class weights) relative to the true prevalence; for random forest the factors were 21.7, 5.2, 5.4 and 8.8. Table 2 and Figure 1 translate this into the language of counselling.

**Table 2.** *Logistic regression at 2% prevalence: children per 1,000 placed in each risk band and children per 1,000 in that band who are truly affected. Means over 20 replications in a population of 50,000 children; "—": no child in the band.*

| Risk band | Children/1,000 (as collected) | Affected/1,000 (as collected) | Children/1,000 (SMOTE, raw) | Affected/1,000 (SMOTE, raw) | Children/1,000 (SMOTE + mean matching) | Affected/1,000 (SMOTE + mean matching) |
|:----------------|:--------:|:--------:|:--------:|:--------:|:--------:|:--------:|
| Below 1% | 285 | 5 | 0 | — | 413 | 7 |
| 1–5% | 657 | 21 | 0 | — | 511 | 23 |
| 5–20% | 58 | 83 | 140 | 4 | 73 | 72 |
| 20% or higher | 0 | — | 860 | 23 | 3 | 164 |

![**Figure 1.** Risk bands of logistic regression at 2% prevalence. (a) Trained as collected: most children are in the 1–5% band, and the true rate in each band lies within the range its label promises. (b) Trained after SMOTE: 86.0% of children are told "20% or higher", although only 23 per 1,000 of them are affected. (c) After mean matching to 2% prevalence, the bands become truthful again without any labels.](p11tl_en_fig1.png){width=16cm}

As collected, the bands were truthful: of 1,000 children told "1–5%", about 21 were affected, and of 1,000 in the "5–20%" band, about 83. After SMOTE, 860 of every 1,000 screened children were told "20% or higher", yet the true rate in that group (23 per 1,000) was almost the community prevalence. The "high" band no longer carried information about the individual child, but it still carried an alarming message to the family. Mean matching to 2% (last columns) restored a band distribution close to the as-collected one.

## 3.3. Capacity-based service: rebalancing does not find more true cases

When the service admitted the top K% of children, logistic regression trained as collected found 8.70 true cases per 100 assessments at K = 5% — 4.4 times the yield of assessing at random (Table 3, Figure 2). Over-sampling, SMOTE and class weights did not change this significantly (9/9 comparisons non-significant after adjustment); under-sampling reduced it slightly but significantly (q ≤ 0.015), because the model then learns from only 200 records. For random forest, over-sampling, SMOTE and class weights **reduced** the number of true cases per 100 assessments at every capacity (9/9 comparisons significant), by 1.8 to 2.5 cases at K = 5%. Scaled to 10,000 screened children and the same 500 assessments, SMOTE made the service miss about 9 additional affected children. The only exception was under-sampling with random forest, which increased the yield from 7.15 to 7.70 cases at K = 5% (q = 0.004): each tree learns from a small, balanced set and the forest memorises less — a regularisation effect rather than a benefit of "balance" as such.

**Table 3.** *True cases per 100 assessments (mean ± SD over 20 replications) when the service admits the K% of children with the highest scores, and sensitivity at K = 5%. \*: differs from training as collected after Benjamini–Hochberg adjustment. Reference: assessing at random yields 2 true cases per 100.*

| Model | Training | K = 2% | K = 5% | K = 10% | Sensitivity at K = 5% |
|:------------------|:----------------|:------------:|:------------:|:------------:|:------------:|
| Logistic regression | As collected | 11.82 ± 0.64 | 8.70 ± 0.35 | 6.76 ± 0.20 | 21.8% |
|  | Under-sampling | 11.20 ± 1.00\* | 8.23 ± 0.49\* | 6.43 ± 0.28\* | 20.6% |
|  | Over-sampling | 11.69 ± 0.80 | 8.65 ± 0.35 | 6.71 ± 0.19 | 21.6% |
|  | SMOTE | 11.74 ± 0.69 | 8.58 ± 0.36 | 6.74 ± 0.21 | 21.5% |
|  | Class weights | 11.75 ± 0.71 | 8.66 ± 0.38 | 6.75 ± 0.19 | 21.7% |
| Random forest | As collected | 9.10 ± 1.02 | 7.15 ± 0.71 | 5.82 ± 0.35 | 17.9% |
|  | Under-sampling | 9.15 ± 1.41 | 7.70 ± 0.71\* | 6.35 ± 0.47\* | 19.2% |
|  | Over-sampling | 4.33 ± 1.23\* | 4.67 ± 1.00\* | 4.40 ± 0.70\* | 11.7% |
|  | SMOTE | 5.85 ± 1.10\* | 5.36 ± 0.85\* | 4.71 ± 0.49\* | 13.4% |
|  | Class weights | 5.52 ± 1.46\* | 5.24 ± 0.95\* | 4.82 ± 0.51\* | 13.1% |

![**Figure 2.** True cases per 100 assessments when the service admits the top 5% (a) or 10% (b) of screened children; error bars are SDs over 20 replications. Dashed line: assessing at random.](p11tl_en_fig2.png){width=16cm}

## 3.4. Threshold-based service: the waiting list explodes

Table 4 and Figure 3 show what happens when the service applies a risk threshold to the probabilities output by the tool. For logistic regression trained after any rebalancing strategy, at least 99.98% of children were referred at the 2% and 5% thresholds: the rule degenerated into "refer all", with exactly that strategy's net benefit (−31.58 per 1,000 at 5%, worse than referring no one). At the 10% threshold, logistic regression after SMOTE still referred 99.3% of children. A service with 5% capacity would receive a list about twenty times its capacity. Random forest after SMOTE referred 47.8% of children at the 5% threshold, with a net benefit of −9.77 per 1,000 versus 0.67 for the as-collected model.

**Table 4.** *Share of children referred · net benefit ×1,000 under the rule "refer when risk ≥ p~t~", 2% prevalence. Means over 20 replications. A net benefit that is positive and above that of "refer all" means the rule is useful at that threshold.*

| Model | Training — output handling | p~t~ = 2% | p~t~ = 5% | p~t~ = 10% |
|:-------------|:-------------------------|:-------------------:|:-------------------:|:-------------------:|
| Refer all |  | 100.0% · 0.00 | 100.0% · −31.58 | 100.0% · −88.89 |
| Logistic regression | As collected — raw | 33.3% · 6.96 | 5.8% · 1.99 | 0.8% · 0.37 |
|  | SMOTE — raw | 100.0% · 0.00 | 100.0% · −31.57 | 99.3% · −88.10 |
|  | SMOTE — prior correction | 31.4% · 6.93 | 8.3% · 1.90 | 2.1% · 0.25 |
|  | SMOTE — mean matching | 29.7% · 6.90 | 7.6% · 1.96 | 1.9% · 0.33 |
|  | Class weights — raw | 100.0% · 0.00 | 100.0% · −31.58 | 99.8% · −88.70 |
|  | Class weights — mean matching | 31.0% · 6.92 | 7.1% · 1.96 | 1.4% · 0.39 |
|  | Under-sampling — prior correction | 33.1% · 6.68 | 5.0% · 1.59 | 0.6% · 0.17 |
| Random forest | As collected — raw | 31.7% · 5.78 | 11.7% · 0.67 | 3.0% · −0.59 |
|  | SMOTE — raw | 65.9% · 4.10 | 47.8% · −9.77 | 32.5% · −23.39 |
|  | SMOTE — prior correction | 3.7% · 1.31 | 0.8% · 0.14 | 0.2% · −0.03 |
|  | SMOTE — mean matching | 24.4% · 4.57 | 10.4% · −0.34 | 4.1% · −2.06 |
|  | Class weights — raw | 87.0% · 1.83 | 71.1% · −18.73 | 53.4% · −42.18 |
|  | Class weights — mean matching | 27.7% · 4.75 | 9.8% · −0.17 | 3.3% · −1.68 |
|  | Under-sampling — prior correction | 35.3% · 6.55 | 6.3% · 1.46 | 1.0% · 0.02 |

![**Figure 3.** Decision curves at 2% prevalence: (a) logistic regression, (b) random forest. For logistic regression the raw SMOTE curve coincides with "refer all", and prior correction and mean matching coincide with the as-collected curve. For random forest, no repair brings SMOTE back to the as-collected curve.](p11tl_en_fig3.png){width=16cm}

## 3.5. Repairing the scale before use: possible for logistic regression, not for random forest

Table 5 compares ways of handling the output of both models trained after SMOTE.

**Table 5.** *Repairing models trained after SMOTE, 2% prevalence: mean risk (true value 0.0200), ECE (mean ± SD over 20 replications), calibration slope (ideal 1; not reported for Platt refits because it is unstable when the fitted coefficient is close to 0), share referred and net benefit at the 5% threshold. The last row for each model is training as collected, raw output.*

| Model | Output handling (after SMOTE) | Mean risk | ECE ×1,000 | Slope | Referred at 5% | NB ×1,000 at 5% |
|:-------------|:------------------------------|:---------:|:--------------:|:--------:|:---------:|:----------:|
| Logistic regression | Raw output | 0.4150 | 395.0 ± 16.9 | 0.91 | 100.0% | −31.57 |
|  | Prior correction (training prevalence known) | 0.0211 | 2.9 ± 1.3 | 0.91 | 8.3% | 1.90 |
|  | Mean matching, assumed 1% | 0.0100 | 10.0 ± 0.0 | 0.91 | 2.0% | 1.35 |
|  | Mean matching, correct prevalence 2% | 0.0200 | 2.8 ± 1.2 | 0.91 | 7.6% | 1.96 |
|  | Mean matching, assumed 4% | 0.0400 | 20.0 ± 0.0 | 0.91 | 23.0% | −0.41 |
|  | Intercept update, n = 100 | 0.0194 | 8.7 ± 5.8 | 1.02 | 8.2% | 1.32 |
|  | Intercept update, n = 200 | 0.0176 | 8.3 ± 4.5 | 0.91 | 6.7% | 1.38 |
|  | Intercept update, n = 500 | 0.0195 | 4.0 ± 1.6 | 0.91 | 7.4% | 1.86 |
|  | Platt refit, n = 500 | 0.0194 | 4.8 ± 2.4 | — | 4.8% | 1.64 |
|  | *Reference: trained as collected* | 0.0200 | 2.3 | 1.16 | 5.8% | 1.99 |
| Random forest | Raw output | 0.1088 | 90.0 ± 6.8 | 0.35 | 47.8% | −9.77 |
|  | Prior correction (training prevalence known) | 0.0039 | 16.1 ± 0.3 | 0.35 | 0.8% | 0.14 |
|  | Mean matching, assumed 1% | 0.0100 | 12.6 ± 1.1 | 0.35 | 4.0% | 0.20 |
|  | Mean matching, correct prevalence 2% | 0.0200 | 14.3 ± 1.4 | 0.35 | 10.4% | −0.34 |
|  | Mean matching, assumed 4% | 0.0400 | 26.4 ± 1.3 | 0.35 | 21.9% | −2.40 |
|  | Intercept update, n = 100 | 0.0206 | 17.4 ± 4.9 | 0.45 | 10.7% | −0.65 |
|  | Intercept update, n = 200 | 0.0182 | 15.4 ± 3.9 | 0.35 | 9.1% | −0.28 |
|  | Intercept update, n = 500 | 0.0193 | 14.4 ± 1.7 | 0.35 | 9.8% | −0.29 |
|  | Platt refit, n = 500 | 0.0195 | 5.0 ± 2.1 | — | 2.5% | 0.03 |
|  | *Reference: trained as collected* | 0.0207 | 8.6 | 0.45 | 11.7% | 0.67 |

**Logistic regression: repairable without labels.** For logistic regression, rebalancing mainly shifted the intercept: the calibration slope stayed close to 1 under every training strategy (0.91–1.22), so the scale was shifted rather than stretched. Prior correction brought the ECE down to 2.1–3.1 per 1,000 and mean matching to 2.1–2.9 per 1,000 for all four rebalancing strategies, and the net benefit after either repair differed from the as-collected model by at most 0.40 per 1,000 at all three thresholds — far smaller than the decisions discussed here, even though a few tiny differences were statistically significant thanks to the paired design.

**Random forest: not repairable by a shift.** After over-sampling, SMOTE and class weights, the calibration slope of random forest fell to 0.29–0.42 (versus 0.45 for the as-collected model, itself already too extreme): trees memorise duplicated or interpolated affected children, so probabilities are stretched as well as shifted. Prior correction then **over-corrects**: mean risk fell to 0.0039, only 3.7% of children were referred at the 2% threshold and the net benefit was 1.31 versus 5.78 per 1,000 for the as-collected model. Mean matching restored a mean risk of exactly 0.0200 but not the shape: the ECE remained 10.9–15.1 per 1,000 and net benefit at the 5% threshold was negative. A notable exception was random forest with **under-sampling**: its slope was 1.00, and after prior correction its net benefit at the 2% threshold was 6.55 per 1,000 — significantly above the as-collected model, in line with Dal Pozzolo et al. (2015).

**A wrong prevalence estimate.** Mean matching needs a prevalence estimate. For logistic regression after SMOTE, using 4% instead of 2% raised the share referred at the 5% threshold to 23.0% and made net benefit negative (−0.41); using 1% lowered the share referred to 2.0% with a net benefit of 1.35 (versus 1.96 with the correct prevalence). At thresholds of 5% and above, under-estimating the prevalence was less harmful than over-estimating it.

**A few local labels are not better than a trustworthy prevalence.** For logistic regression after SMOTE, an intercept update on 100 or 200 labelled records — only about 1.9 and 3.4 affected children — gave an ECE of 8.7 and 8.3 per 1,000, worse than mean matching to the correct prevalence (2.8), because the number of affected children in a small sample fluctuates strongly. For logistic regression, a full Platt refit was worse still and unstable: the fitted Platt slope was negative — so the repair **reversed** the ranking — in 23/180 fits with n = 100, 20/200 with n = 200 and 3/200 with n = 500; with n = 100, 2 replications contained no affected child and could not be fitted. With 500 records (about 9.7 affected children) the intercept update narrowed the gap (4.0 per 1,000) but did not yet match mean matching to the correct prevalence. For random forest after SMOTE, a Platt refit on 500 records was the only option in Table 5 that repaired most of the shape distortion (ECE 5.0 per 1,000), but its net benefit at the 5% threshold was still only 0.03 versus 0.67 for the as-collected model: recalibration cannot restore the ranking lost in Section 3.3.

## 3.6. The audit tool on three hypothetical vendors

We ran the tool of Section 2.7 on three hypothetical models with a service capacity of 5%. **Vendor A** (logistic regression after SMOTE; the service has only 5,000 unlabelled scores): the tool reported an inflation factor of 18.7 and a referral share of 99.7% at the 5% threshold (above capacity), falling to 8.2% after mean matching; the number of children per 1,000 in the "20% or higher" band fell from 747 to 7. **Vendor B** (random forest after SMOTE; 1,000 labelled records with 24 affected children): inflation factor 4.7; after mean matching the net benefit at the 5% threshold rose from −5.00 to 0.37 per 1,000, but the calibration slope was only 0.29 and the tool warned of a shape distortion — that is, the service should ask for a model that was not rebalanced. **Vendor C** (logistic regression trained as collected; the same 1,000 labelled records): inflation factor 0.96, slope 0.80, and the expected 2% prevalence lay inside the Wilson interval 0.016–0.035; the only warning was that the 5% threshold referred 7.4% of children, above the 5% capacity — a threshold decision the service must make, not a defect of the tool.

# 4. DISCUSSION

## 4.1. Implications for psychological services

The results can be summarised in one sentence: **rebalancing the training data is a technical decision of the developer, but its consequences land in the counselling room and on the waiting list.** Three consequences stand out.

*First, the figure told to families loses its meaning.* A tool trained after SMOTE put most children in a "high" risk band and none in the low bands (Table 2). If that figure is read out to parents, most families leave with a level of worry that does not match the real risk — a psychological harm that guidance on risk communication tries to prevent (Zipkin et al., 2014; Spiegelhalter, 2017). Conversely, when almost every child is flagged, the alert loses its force for professionals too — the alert fatigue described for clinical decision-support systems (Ancker et al., 2017).

*Second, the waiting list is set by the risk scale rather than by capacity.* If the service applies a risk threshold to the output of a rebalanced model, referrals can exceed capacity many times over (Table 4). In practice this rarely leads to assessing everyone; it leads to long queues, first-come-first-served ordering instead of risk-based ordering, and the loss of the very benefit the tool was bought to deliver.

*Third, rebalancing does not buy more true cases.* When the service admits children up to capacity — the only mode of operation that does not depend on the scale — rebalancing did not help logistic regression and made random forest worse, except under-sampling (Table 3). The belief that rebalancing "makes the model more sensitive to the minority class" confuses **sensitivity at a default cut-off of 0.5** with **ranking ability**: for logistic regression, rebalancing essentially moves the cut-off — something the service can do directly by choosing a threshold or a capacity; for random forest it also damages the ranking itself.

We therefore propose six questions a psychological service should put to a vendor before deployment (Table 6). They do not require psychologists to understand the algorithm; they require vendors to be transparent about what was done to the data, and they let the service check the answers itself with the tool of Section 2.7.

**Table 6.** *Six questions a psychological service should ask the vendor of a screening tool, and how to use the answers.*

| Question | Why ask | If the answer is… |
|:------------------------------|:------------------------------|:------------------------------|
| 1\. Was the model trained on rebalanced data (under- or over-sampling, SMOTE, class weights)? | Rebalancing inflates every probability (Section 3.2). | "Yes": do not read probabilities to families before repairing the scale. |
| 2\. What were the prevalences in the original training data and after rebalancing? | Needed for prior correction, Equation (2). | Unknown: use mean matching, Equation (3). |
| 3\. What kind of model is it? | Logistic regression can be repaired by a shift; random forest after over-sampling, SMOTE or class weights cannot (Section 3.5). | A tree ensemble after over-sampling, SMOTE or class weights: ask for a version that was not rebalanced, or for under-sampling with prior correction. |
| 4\. At what prevalence was calibration checked? | Community prevalence differs from that of the development sample. | Not at community prevalence: run the audit tool on the service's own unlabelled scores. |
| 5\. What is the default referral threshold, and what share of children does it refer? | Referral load must match assessment capacity. | Above capacity: choose another threshold, or run the service by capacity (admit the top K%). |
| 6\. Are local labels needed, and how many? | With fewer than a few hundred labelled records, updating is worse than a trustworthy prevalence (Section 3.5). | Prefer a trustworthy prevalence estimate; consider refitting only with about 500 records and at least 10 affected children. |

## 4.2. Why logistic regression can be repaired and random forest cannot

For a model that estimates the conditional probability correctly, rebalancing the training set only changes the prior; on the log-odds scale this adds a constant, and Equation (2) or (3) subtracts that constant again (Elkan, 2001; Saerens et al., 2002). Logistic regression is close to this ideal: class weights and over-sampling change little besides the intercept. Random forest is not. Over-sampling and SMOTE place many copies or near-copies of the same affected children in the training set; leaves become "pure" around those points, and the forest's probabilities are pushed towards the extremes. This is a distortion of **shape**, visible as a calibration slope far from 1, and no monotone shift — not even Bayes' rule, correct in theory — can repair it; prior correction even over-corrects, because its assumption is violated. These findings agree with the simulations of van den Goorbergh et al. (2022) for logistic regression and Carriero et al. (2025) for machine-learning models, and with the recommendation of Dal Pozzolo et al. (2015) to combine under-sampling with prior correction for tree-based models.

## 4.3. Context

The Vietnamese field study (Vo et al., 2026) reported a very high AUC for random forest with SMOTE; this simulation does not contradict that result — the data and models differ — but suggests that when such a model enters a service, the share of children referred, the net benefit at the threshold the service actually uses, and calibration at community prevalence should be reported as well. The same lesson comes from the M-CHAT-R/F, whose pooled positive predictive value in community samples is considerably lower than in high-prevalence samples (Aishworiya et al., 2023). A companion study on probability calibration ([Author], 2026c) showed that the scores of a fuzzy inference system are not probabilities either; the present study adds a different source of distortion, one that can affect any machine-learning model and that is created by the training procedure itself.

## 4.4. Limitations

First, all results come from **synthetic data**: the mechanical phenomena (inflation, degeneration into "refer all", exact prior correction for regression-type models) do not depend on the generator, but specific magnitudes — true cases per 100 assessments, the size of the random-forest loss — depend on the structure of the simulated data and may differ in real children. Second, both models discriminate only moderately on these data (AUC about 0.69–0.73); with better-discriminating models the gaps between modes of operation may differ. Third, the three new analyses consider one prevalence (2%) and two models; the full grid of the companion study covers four prevalences and four models. Fourth, hyperparameters were fixed (200 trees, five records per leaf); a more strongly regularised random forest may be less extreme. Fifth, labels in the audit samples were assumed to be error-free specialist assessments; in practice labels have error and are usually available only for referred children (verification bias), which makes updating on local labels even harder than simulated. Sixth, the four risk bands, the capacity levels and the tool's warning thresholds are illustrative conventions; a given service should substitute its own. Finally, the study did not measure psychological effects on families; the arguments about worry and alert fatigue rest on the literature, not on data from this study.

# 5. CONCLUSION

On synthetic data at 2% prevalence, training a screening tool on rebalanced data did not help a psychological service find more affected children, but it inflated the risk figure told to families more than twentyfold and made a threshold-based referral rule send almost every child to the waiting list. For logistic regression the service can repair this almost completely with a label-free log-odds shift, given only a trustworthy prevalence estimate; for random forest after over-sampling, SMOTE or class weights it cannot, and a version without rebalancing should be requested. In practice: ask the vendor the six questions of Table 6, check the inflation factor and referral load on the service's own population before deployment, and, where possible, run the service by capacity rather than by an unchecked probability threshold. These conclusions need to be verified on real screening data before they are applied.

# DECLARATIONS

**Ethics.** The study used only machine-generated synthetic data; no data from any child or family were involved, so ethical review was not required.

**Data and code availability.** All code, the synthetic record pools (`_p11_pool.npz`), result files, the audit tool and the manuscript build scripts are available at [GitHub link — to be added after upload]. `python src/run_p11_tl.py` reproduces every number in Sections 3.2–3.5 (about 10 minutes); `python src/p11_referral_audit.py --demo` reproduces Section 3.6. Two runs produce byte-identical result files.

**Related publications.** The main grid in Section 3.1 and Table 1 is reported in full in two companion manuscripts by the same authors ([Author], 2026a; [Author], 2026b); the analyses in Sections 3.2–3.6, Tables 2–6 and Figures 1–3 are new. A Vietnamese-language version of this article, sharing its data and results, has been prepared for a national journal; the relationship between the manuscripts will be disclosed to the editors.

**Conflicts of interest.** The authors declare no conflicts of interest.

**Funding.** [To be completed.]

**Author contributions.** [To be completed following CRediT.]

# REFERENCES

Aishworiya, R., Ma, V. K., Stewart, S., Hagerman, R., & Feldman, H. M. (2023). Meta-analysis of the Modified Checklist for Autism in Toddlers, Revised/Follow-up for screening. *Pediatrics, 151*(6), e2022059393. https://doi.org/10.1542/peds.2022-059393

Ancker, J. S., Edwards, A., Nosal, S., Hauser, D., Mauer, E., Kaushal, R., & the HITEC Investigators. (2017). Effects of workload, work complexity, and repeated alerts on alert fatigue in a clinical decision support system. *BMC Medical Informatics and Decision Making, 17*, 36. https://doi.org/10.1186/s12911-017-0430-8

[Author]. (2026a). *Resampling or threshold moving? Class imbalance, calibration and decision curves for developmental screening at community prevalence — A simulation study* [Manuscript submitted for publication].

[Author]. (2026b). *Tái lấy mẫu hay dịch chuyển ngưỡng: Xử lý mất cân bằng lớp trong sàng lọc phát triển ở tỷ lệ hiện mắc cộng đồng* [Resampling or threshold moving: Handling class imbalance in developmental screening at community prevalence] [Manuscript submitted for publication].

[Author]. (2026c). *Con số nguy cơ trên màn hình có nghĩa là gì? Hiệu chỉnh xác suất để công cụ số hỗ trợ nhà tâm lý lâm sàng truyền đạt nguy cơ và quyết định chuyển đánh giá trong sàng lọc phát triển* [What does the risk number on the screen mean? Probability calibration so that digital tools can support clinical psychologists in communicating risk and deciding on referral in developmental screening] [Manuscript submitted for publication].

Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological), 57*(1), 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x

Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. https://doi.org/10.1023/A:1010933404324

Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review, 78*(1), 1–3. https://doi.org/10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2

Carriero, A., Luijken, K., de Hond, A., Moons, K. G. M., van Calster, B., & van Smeden, M. (2025). The harms of class imbalance corrections for machine learning based prediction models: A simulation study. *Statistics in Medicine, 44*(3–4), e10320. https://doi.org/10.1002/sim.10320

Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic minority over-sampling technique. *Journal of Artificial Intelligence Research, 16*, 321–357. https://doi.org/10.1613/jair.953

Collins, G. S., Moons, K. G. M., Dhiman, P., Riley, R. D., Beam, A. L., Van Calster, B., Ghassemi, M., Liu, X., Reitsma, J. B., van Smeden, M., Boulesteix, A.-L., Camaradou, J. C., Celi, L. A., Denaxas, S., Denniston, A. K., Glocker, B., Golub, R. M., Harvey, H., Heinze, G., … Logullo, P. (2024). TRIPOD+AI statement: Updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ, 385*, e078378. https://doi.org/10.1136/bmj-2023-078378

Dal Pozzolo, A., Caelen, O., Johnson, R. A., & Bontempi, G. (2015). Calibrating probability with undersampling for unbalanced classification. In *2015 IEEE Symposium Series on Computational Intelligence* (pp. 159–166). IEEE. https://doi.org/10.1109/SSCI.2015.33

Elkan, C. (2001). The foundations of cost-sensitive learning. In *Proceedings of the Seventeenth International Joint Conference on Artificial Intelligence* (pp. 973–978). Morgan Kaufmann.

Fernández, A., García, S., Herrera, F., & Chawla, N. V. (2018). SMOTE for learning from imbalanced data: Progress and challenges, marking the 15-year anniversary. *Journal of Artificial Intelligence Research, 61*, 863–905. https://doi.org/10.1613/jair.1.11192

Gigerenzer, G., & Hoffrage, U. (1995). How to improve Bayesian reasoning without instruction: Frequency formats. *Psychological Review, 102*(4), 684–704. https://doi.org/10.1037/0033-295X.102.4.684

Grove, W. M., Zald, D. H., Lebow, B. S., Snitz, B. E., & Nelson, C. (2000). Clinical versus mechanical prediction: A meta-analysis. *Psychological Assessment, 12*(1), 19–30. https://doi.org/10.1037/1040-3590.12.1.19

He, H., & Garcia, E. A. (2009). Learning from imbalanced data. *IEEE Transactions on Knowledge and Data Engineering, 21*(9), 1263–1284. https://doi.org/10.1109/TKDE.2008.239

Hyman, S. L., Levy, S. E., Myers, S. M., & Council on Children with Disabilities, Section on Developmental and Behavioral Pediatrics. (2020). Identification, evaluation, and management of children with autism spectrum disorder. *Pediatrics, 145*(1), e20193447. https://doi.org/10.1542/peds.2019-3447

Janssen, K. J. M., Moons, K. G. M., Kalkman, C. J., Grobbee, D. E., & Vergouwe, Y. (2008). Updating methods improved the performance of a clinical prediction model in new patients. *Journal of Clinical Epidemiology, 61*(1), 76–86. https://doi.org/10.1016/j.jclinepi.2007.04.018

Lewis, C. C., Boyd, M., Puspitasari, A., Navarro, E., Howard, J., Kassab, H., Hoffman, M., Scott, K., Lyon, A., Douglas, S., Simon, G., & Kroenke, K. (2019). Implementing measurement-based care in behavioral health: A review. *JAMA Psychiatry, 76*(3), 324–335. https://doi.org/10.1001/jamapsychiatry.2018.3329

Ministry of Health of Viet Nam. (2021). *Decision No. 2254/QĐ-BYT of 7 May 2021 promulgating the toolkit for early detection of autism spectrum disorder in children* [in Vietnamese]. Hanoi.

Morris, T. P., White, I. R., & Crowther, M. J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine, 38*(11), 2074–2102. https://doi.org/10.1002/sim.8086

Nguyen, D. H. (2026). *Mô hình lai luật – học máy với đầu ra mờ hỗ trợ sàng lọc sớm nguy cơ rối loạn phổ tự kỷ ở trẻ 0–36 tháng* [A hybrid rule-based/machine-learning model with fuzzy outputs to support early screening for autism spectrum disorder risk in children aged 0–36 months] [Master's thesis]. Lac Hong University.

Robins, D. L., Casagrande, K., Barton, M., Chen, C.-M. A., Dumont-Mathieu, T., & Fein, D. (2014). Validation of the Modified Checklist for Autism in Toddlers, Revised with Follow-up (M-CHAT-R/F). *Pediatrics, 133*(1), 37–45. https://doi.org/10.1542/peds.2013-1813

Saerens, M., Latinne, P., & Decaestecker, C. (2002). Adjusting the outputs of a classifier to new a priori probabilities: A simple procedure. *Neural Computation, 14*(1), 21–41. https://doi.org/10.1162/089976602753284446

Spiegelhalter, D. (2017). Risk and uncertainty communication. *Annual Review of Statistics and Its Application, 4*, 31–60. https://doi.org/10.1146/annurev-statistics-010814-020148

Steyerberg, E. W., Borsboom, G. J. J. M., van Houwelingen, H. C., Eijkemans, M. J. C., & Habbema, J. D. F. (2004). Validation and updating of predictive logistic regression models: A study on sample size and shrinkage. *Statistics in Medicine, 23*(16), 2567–2586. https://doi.org/10.1002/sim.1844

Sutton, R. T., Pincock, D., Baumgart, D. C., Sadowski, D. C., Fedorak, R. N., & Kroeker, K. I. (2020). An overview of clinical decision support systems: Benefits, risks, and strategies for success. *npj Digital Medicine, 3*, 17. https://doi.org/10.1038/s41746-020-0221-y

Torous, J., Bucci, S., Bell, I. H., Kessing, L. V., Faurholt-Jepsen, M., Whelan, P., Carvalho, A. F., Keshavan, M., Linardon, J., & Firth, J. (2021). The growing field of digital psychiatry: Current evidence and the future of apps, social media, chatbots, and virtual reality. *World Psychiatry, 20*(3), 318–335. https://doi.org/10.1002/wps.20883

Van Calster, B., McLernon, D. J., van Smeden, M., Wynants, L., & Steyerberg, E. W. (2019). Calibration: The Achilles heel of predictive analytics. *BMC Medicine, 17*, 230. https://doi.org/10.1186/s12916-019-1466-7

Van Calster, B., Nieboer, D., Vergouwe, Y., De Cock, B., Pencina, M. J., & Steyerberg, E. W. (2016). A calibration hierarchy for risk models was defined: From utopia to empirical data. *Journal of Clinical Epidemiology, 74*, 167–176. https://doi.org/10.1016/j.jclinepi.2015.12.005

van den Goorbergh, R., van Smeden, M., Timmerman, D., & Van Calster, B. (2022). The harm of class imbalance corrections for risk prediction models: Illustration and simulation using logistic regression. *Journal of the American Medical Informatics Association, 29*(9), 1525–1534. https://doi.org/10.1093/jamia/ocac093

Vickers, A. J., & Elkin, E. B. (2006). Decision curve analysis: A novel method for evaluating prediction models. *Medical Decision Making, 26*(6), 565–574. https://doi.org/10.1177/0272989X06295361

Vickers, A. J., Van Calster, B., & Steyerberg, E. W. (2016). Net benefit approaches to the evaluation of prediction models, molecular markers, and diagnostic tests. *BMJ, 352*, i6. https://doi.org/10.1136/bmj.i6

Vo, T. V., Nguyen, P. M., Nguyen, D. N., Nguyen, T. V., Thai, D. M., Ly, H. H. V., & Luu, T. N. N. (2026). Machine learning–assisted autism risk stratification in toddlers using the Vietnamese M-CHAT-R and perinatal predictors: A cross-sectional study in Vietnam. *Journal of Autism and Developmental Disorders*. Advance online publication. https://doi.org/10.1007/s10803-026-07227-1

Wynants, L., van Smeden, M., McLernon, D. J., Timmerman, D., Steyerberg, E. W., & Van Calster, B. (2019). Three myths about risk thresholds for prediction models. *BMC Medicine, 17*, 192. https://doi.org/10.1186/s12916-019-1425-3

Zeidan, J., Fombonne, E., Scorah, J., Ibrahim, A., Durkin, M. S., Saxena, S., Yusuf, A., Shih, A., & Elsabbagh, M. (2022). Global prevalence of autism: A systematic review update. *Autism Research, 15*(5), 778–790. https://doi.org/10.1002/aur.2696

Zipkin, D. A., Umscheid, C. A., Keating, N. L., Allen, E., Aung, K., Beyth, R., Kaatz, S., Mann, D. M., Sussman, J. B., Korenstein, D., Schardt, C., Nagi, A., Sloane, R., & Feldstein, D. A. (2014). Evidence-based risk communication: A systematic review. *Annals of Internal Medicine, 161*(4), 270–280. https://doi.org/10.7326/M14-0295
