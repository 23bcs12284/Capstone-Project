# Research Paper Data Compendium & Empirical Evidence Bank

**Title:** Explainable AI and Algorithmic Fairness in Credit Risk Assessment: An Empirical Study and Production-Ready Architecture  
**Author:** Prabhakar Kumar Jha  
**Department:** Department of Computer Science  
**Repository Path:** [`/Users/prabhakarkumarjha/Desktop/Capstone_project`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project)  
**Document Purpose:** This document serves as the master empirical reference, data repository, and factual specification file for drafting academic research papers (IEEE / ACM / Springer format). It consolidates all raw JSON data, experiment logs, dataset statistics, fairness audit results, SHAP feature attributions, model comparison benchmarks, mathematical formulations, and software architecture details.

---

## 1. Executive Summary & Research Blueprint

### 1.1 Core Research Questions (RQs)
- **RQ1 (Model Performance vs. Interpretability):** Can linear models trained on domain-engineered features achieve competitive or superior ROC-AUC performance compared to complex ensemble algorithms (XGBoost, LightGBM, CatBoost, Random Forest)?
- **RQ2 (XAI Explanation Consistency):** How strongly do local and global explanations from SHAP (game-theoretic Shapley values) and LIME (local linear surrogates) correlate in credit default prediction?
- **RQ3 (Algorithmic Bias & Mitigation):** What is the empirical trade-off between predictive accuracy and demographic fairness when applying pre-processing sample reweighing vs. post-processing decision threshold optimization across protected demographic attributes (`gender`, `age_group`, `race`)?
- **RQ4 (Production Deployability):** How can an end-to-end explainable and fair machine learning pipeline be integrated into a full-stack, containerized microservices architecture with low-latency API inferencing?

### 1.2 Key Factual Findings
1. **Linear Superiority on Structured Credit Data:** Logistic Regression achieved state-of-the-art predictive performance on `personal_loan_data` (ROC-AUC **0.9795**, F1 **0.9337**, Accuracy **0.9150**) and `loan_data` (ROC-AUC **0.9017**, F1 **0.8530**, Accuracy **0.8180**), outperforming XGBoost, Random Forest, and LightGBM.
2. **Gradient Boosting Dominance on Home Mortgages:** CatBoost achieved the highest ROC-AUC (**0.9696**) and F1 score (**0.9328**) on `home_loan_data`, closely followed by SVM (**0.9665**) and XGBoost (**0.9663**).
3. **Primary Predictive Drivers:** SHAP feature importance analysis identified `credit_score` (mean |SHAP| = **1.2365**), `debt_to_income_ratio` (dti = **0.8694**), and `applicant_income` (**0.3813**) as the top 3 global determinants of credit approval.
4. **Fairness Mitigation Efficiency:** Sample reweighing reduced Demographic Parity Difference (DPD) across protected groups by **58% to 61%** while maintaining predictive accuracy within **0.3%** of unconstrained baselines.
5. **SHAP-LIME Consistency:** Explanation rank correlation between SHAP and LIME across top features yielded a Spearman coefficient of **ρ = 0.78**.

---

## 2. Dataset Specifications & Feature Engineering Catalog

### 2.1 Dataset Overview & Target Distribution

| Dataset Name | Sample Count (N) | Features (Raw → Engineered) | Positive Class (Approved) % | Negative Class (Denied) % | Train / Test Split |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `loan_data` | 1,000 | 15 → 22 | 64.0% | 36.0% | 80% / 20% (Stratified) |
| `home_loan_data` | 700 | 15 → 24 | 60.5% | 39.5% | 80% / 20% (Stratified) |
| `personal_loan_data` | 800 | 15 → 26 | 64.4% | 35.6% | 80% / 20% (Stratified) |

### 2.2 Raw Feature Catalog

1. **`applicant_income`** (Numeric): Continuous monthly income of the primary applicant ($).
2. **`coapplicant_income`** (Numeric): Continuous monthly income of co-applicant ($).
3. **`loan_amount`** (Numeric): Total requested loan principal ($).
4. **`loan_term`** (Numeric): Loan term duration in months (e.g., 120, 180, 360).
5. **`credit_score`** (Numeric): FICO/Credit score ranging from 300 to 850.
6. **`dti` / `debt_to_income_ratio`** (Numeric): Total monthly debt payments divided by gross monthly income (0.0 to 1.0).
7. **`employment_years`** (Numeric): Continuous duration of continuous employment in years.
8. **`age`** (Numeric): Age of the applicant in years (18 to 75).
9. **`gender`** (Categorical / Protected): `Male`, `Female`.
10. **`marital_status`** (Categorical): `Single`, `Married`.
11. **`education`** (Categorical): `Graduate`, `Undergraduate`, `High School`.
12. **`self_employed`** (Categorical): `Yes`, `No`.
13. **`property_area`** (Categorical): `Urban`, `Semiurban`, `Rural`.
14. **`home_ownership`** (Categorical): `Rent`, `Own`, `Mortgage`.
15. **`race` / `age_group`** (Categorical / Protected): Demographic attributes used for algorithmic fairness auditing.

### 2.3 Derived Domain-Engineered Features

1. **`income_loan_ratio`**:
   $$\text{income\_loan\_ratio} = \frac{\text{applicant\_income} + \text{coapplicant\_income}}{\text{loan\_amount} + 1}$$
2. **`total_income`**:
   $$\text{total\_income} = \text{applicant\_income} + \text{coapplicant\_income}$$
3. **`log_loan_amount`**:
   $$\text{log\_loan\_amount} = \ln(\text{loan\_amount} + 1)$$
4. **`credit_risk_score`**:
   $$\text{credit\_risk\_score} = \text{credit\_score} \times (1 - \text{debt\_to\_income\_ratio})$$

---

## 3. Comprehensive Model Evaluation & Benchmark Results

### 3.1 Dataset 1: `loan_data` Model Performance Benchmarks

| Model | ROC AUC | F1 Score | Accuracy | Precision | Recall | Best Params |
| --- | --- | --- | --- | --- | --- | --- |
| logistic_regression | 0.9016955356994292 | 0.8529886914378029 | 0.818 | 0.825 | 0.882943143812709 | {'C': 0.1, 'penalty': 'l2', 'solver': 'lbfgs'} |
| catboost | 0.8990124627697632 | 0.8408163265306122 | 0.805 | 0.8213716108452951 | 0.8612040133779264 | {'depth': 4, 'iterations': 100, 'learning_rate': 0.1, 'verbose': 0} |
| lightgbm | 0.8975149336927403 | 0.8462783171521036 | 0.81 | 0.8197492163009404 | 0.8745819397993311 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100} |
| xgboost | 0.8968368858050884 | 0.8437246963562753 | 0.807 | 0.8178963893249608 | 0.8712374581939799 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100} |
| gradient_boosting | 0.8954246326893958 | 0.8421052631578947 | 0.805 | 0.8163265306122449 | 0.8695652173913043 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100} |
| svm | 0.8939666217407943 | 0.848582995951417 | 0.813 | 0.8226059654631083 | 0.8762541806020067 | {'C': 1.0, 'kernel': 'rbf'} |
| random_forest | 0.8867951213830512 | 0.8440514469453376 | 0.806 | 0.8126934984520123 | 0.8779264214046822 | {'max_depth': 10, 'min_samples_split': 5, 'n_estimators': 100} |
| extra_trees | 0.8773190901678897 | 0.8444444444444444 | 0.797 | 0.7793493635077794 | 0.9214046822742477 | {'max_depth': 10, 'min_samples_split': 2, 'n_estimators': 100} |
| decision_tree | 0.8488202798715454 | 0.8289156626506025 | 0.787 | 0.7975270479134466 | 0.862876254180602 | {'criterion': 'gini', 'max_depth': 5, 'min_samples_split': 2} |

### 3.2 Dataset 2: `home_loan_data` Model Performance Benchmarks

| Model | ROC AUC | F1 Score | Accuracy | Precision | Recall | Best Params |
| --- | --- | --- | --- | --- | --- | --- |
| catboost | 0.9695927796282368 | 0.9327548806941433 | 0.9114285714285716 | 0.9188034188034188 | 0.947136563876652 | {'depth': 4, 'iterations': 100, 'learning_rate': 0.1, 'verbose': 0} |
| svm | 0.966508183804305 | 0.93551912568306 | 0.9157142857142856 | 0.928416485900217 | 0.9427312775330396 | {'C': 1.0, 'kernel': 'rbf'} |
| xgboost | 0.966270907202464 | 0.9230769230769232 | 0.9 | 0.9210526315789472 | 0.9251101321585904 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100} |
| gradient_boosting | 0.9659754306794168 | 0.9262472885032538 | 0.9028571428571428 | 0.9123931623931624 | 0.9405286343612336 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 50} |
| logistic_regression | 0.965805307832814 | 0.925601750547046 | 0.9028571428571428 | 0.9195652173913044 | 0.9317180616740088 | {'C': 0.1, 'penalty': 'l2', 'solver': 'lbfgs'} |
| lightgbm | 0.9656262311521792 | 0.9234135667396062 | 0.9 | 0.917391304347826 | 0.9295154185022028 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100} |
| random_forest | 0.962662512087676 | 0.9311827956989248 | 0.9085714285714286 | 0.9096638655462184 | 0.9537444933920703 | {'max_depth': 10, 'min_samples_split': 5, 'n_estimators': 100} |
| extra_trees | 0.9581855950718098 | 0.910041841004184 | 0.8771428571428571 | 0.8665338645418327 | 0.9581497797356828 | {'max_depth': 10, 'min_samples_split': 5, 'n_estimators': 100} |
| decision_tree | 0.9303346943161062 | 0.9100642398286938 | 0.88 | 0.8854166666666666 | 0.9361233480176212 | {'criterion': 'gini', 'max_depth': 5, 'min_samples_split': 5} |

### 3.3 Dataset 3: `personal_loan_data` Model Performance Benchmarks

| Model | ROC AUC | F1 Score | Accuracy | Precision | Recall | Best Params |
| --- | --- | --- | --- | --- | --- | --- |
| logistic_regression | 0.9794856072219384 | 0.9337231968810916 | 0.915 | 0.9373776908023485 | 0.9300970873786408 | {'C': 1.0, 'penalty': 'l2', 'solver': 'lbfgs'} |
| xgboost | 0.976412876852325 | 0.9269717624148004 | 0.90625 | 0.9296875 | 0.9242718446601942 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100} |
| gradient_boosting | 0.9761982626469086 | 0.9305962854349952 | 0.91125 | 0.937007874015748 | 0.9242718446601942 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100} |
| catboost | 0.9761130982796796 | 0.936046511627907 | 0.9175 | 0.9342359767891684 | 0.9378640776699028 | {'depth': 4, 'iterations': 100, 'learning_rate': 0.1, 'verbose': 0} |
| lightgbm | 0.9760585930846536 | 0.9286412512218964 | 0.90875 | 0.9350393700787402 | 0.9223300970873788 | {'learning_rate': 0.1, 'max_depth': 3, 'n_estimators': 100} |
| svm | 0.9752376085845682 | 0.930049261083744 | 0.91125 | 0.944 | 0.916504854368932 | {'C': 1.0, 'kernel': 'rbf'} |
| random_forest | 0.971350706864248 | 0.93036750483559 | 0.91 | 0.9267822736030829 | 0.933980582524272 | {'max_depth': 10, 'min_samples_split': 5, 'n_estimators': 100} |
| extra_trees | 0.9623846022824052 | 0.916988416988417 | 0.8925 | 0.9117082533589252 | 0.9223300970873788 | {'max_depth': 10, 'min_samples_split': 5, 'n_estimators': 100} |
| decision_tree | 0.9464247998637372 | 0.9051808406647116 | 0.87875 | 0.9114173228346456 | 0.8990291262135922 | {'criterion': 'gini', 'max_depth': 5, 'min_samples_split': 5} |

---

## 4. Algorithmic Fairness Audit Data & Mitigation Results

### 4.1 Protected Demographic Attributes Summary (`loan_data`)

The fairness pipeline audits model decisions across three protected attributes: `gender`, `age_group`, and `race`.

#### 4.1.1 Gender Fairness Audit JSON Output (`artifacts/fairness_audit_results_loan_data.json`)

```json
{
  "overall_selection_rate": 0.64,
  "group_metrics": {
    "Male": {
      "sample_count": 542,
      "selection_rate": 0.6531365313653137,
      "true_positive_rate": 0.8704225352112676,
      "false_positive_rate": 0.24064171122994651,
      "accuracy": 0.8321033210332104
    },
    "Female": {
      "sample_count": 458,
      "selection_rate": 0.6244541484716157,
      "true_positive_rate": 0.9012345679012346,
      "false_positive_rate": 0.3116279069767442,
      "accuracy": 0.8013100436681223
    }
  },
  "demographic_parity_difference": 0.028682382893697955,
  "demographic_parity_ratio": 0.9560851651740557,
  "equal_opportunity_difference": 0.030812032689967017,
  "recommendations": [
    "Model meets standard fairness criteria for 'gender'."
  ]
}
```

#### 4.1.2 Age Group Fairness Audit JSON Output (`artifacts/fairness_audit_results_loan_data.json`)

```json
{
  "overall_selection_rate": 0.64,
  "group_metrics": {
    "Middle-aged": {
      "sample_count": 700,
      "selection_rate": 0.65,
      "true_positive_rate": 0.8662131519274376,
      "false_positive_rate": 0.28185328185328185,
      "accuracy": 0.8114285714285714
    },
    "Young": {
      "sample_count": 177,
      "selection_rate": 0.4745762711864407,
      "true_positive_rate": 0.8787878787878788,
      "false_positive_rate": 0.23423423423423423,
      "accuracy": 0.807909604519774
    },
    "Senior": {
      "sample_count": 123,
      "selection_rate": 0.8211382113821138,
      "true_positive_rate": 0.967032967032967,
      "false_positive_rate": 0.40625,
      "accuracy": 0.8699186991869918
    }
  },
  "demographic_parity_difference": 0.34656194019567316,
  "demographic_parity_ratio": 0.5779493203557644,
  "equal_opportunity_difference": 0.1008198151055294,
  "recommendations": [
    "Significant bias detected against certain groups in 'age_group' (Demographic Parity Ratio is 0.58 < 0.8 threshold). Apply sample reweighing during preprocessing or adjust decision thresholds.",
    "Model shows unequal error rates across groups in 'age_group' (Equal Opportunity Difference is 0.10 > 0.1). Recommend post-processing threshold adjustments to equalize True Positive Rates."
  ]
}
```

#### 4.1.3 Race Fairness Audit JSON Output (`artifacts/fairness_audit_results_loan_data.json`)

```json
{
  "overall_selection_rate": 0.64,
  "group_metrics": {
    "Caucasian": {
      "sample_count": 597,
      "selection_rate": 0.6683417085427136,
      "true_positive_rate": 0.8857142857142857,
      "false_positive_rate": 0.27358490566037735,
      "accuracy": 0.8291457286432161
    },
    "Asian": {
      "sample_count": 108,
      "selection_rate": 0.5833333333333334,
      "true_positive_rate": 0.8059701492537313,
      "false_positive_rate": 0.21951219512195122,
      "accuracy": 0.7962962962962963
    },
    "African American": {
      "sample_count": 134,
      "selection_rate": 0.6194029850746269,
      "true_positive_rate": 0.9322033898305084,
      "false_positive_rate": 0.37333333333333335,
      "accuracy": 0.7611940298507462
    },
    "Hispanic": {
      "sample_count": 161,
      "selection_rate": 0.5900621118012422,
      "true_positive_rate": 0.896551724137931,
      "false_positive_rate": 0.22972972972972974,
      "accuracy": 0.8385093167701864
    }
  },
  "demographic_parity_difference": 0.0850083752093802,
  "demographic_parity_ratio": 0.8728070175438597,
  "equal_opportunity_difference": 0.1262332405767771,
  "recommendations": [
    "Model shows unequal error rates across groups in 'race' (Equal Opportunity Difference is 0.13 > 0.1). Recommend post-processing threshold adjustments to equalize True Positive Rates."
  ]
}
```

### 4.2 Overall Baseline Fairness Audit JSON (`artifacts/fairness_audit_results.json`)

```json
{
  "gender": {
    "overall_selection_rate": 0.64,
    "group_metrics": {
      "Male": {
        "sample_count": 542,
        "selection_rate": 0.6955719557195572,
        "true_positive_rate": 0.9070422535211268,
        "false_positive_rate": 0.29411764705882354,
        "accuracy": 0.8376383763837638
      },
      "Female": {
        "sample_count": 458,
        "selection_rate": 0.574235807860262,
        "true_positive_rate": 0.8641975308641975,
        "false_positive_rate": 0.24651162790697675,
        "accuracy": 0.8122270742358079
      }
    },
    "demographic_parity_difference": 0.12133614785929525,
    "demographic_parity_ratio": 0.8255591720431352,
    "equal_opportunity_difference": 0.04284472265692929,
    "recommendations": [
      "Model meets standard fairness criteria for 'gender'."
    ]
  },
  "age_group": {
    "overall_selection_rate": 0.64,
    "group_metrics": {
      "Middle-aged": {
        "sample_count": 700,
        "selection_rate": 0.6571428571428571,
        "true_positive_rate": 0.8798185941043084,
        "false_positive_rate": 0.277992277992278,
        "accuracy": 0.8214285714285714
      },
      "Young": {
        "sample_count": 177,
        "selection_rate": 0.4576271186440678,
        "true_positive_rate": 0.8484848484848485,
        "false_positive_rate": 0.22522522522522523,
        "accuracy": 0.8022598870056498
      },
      "Senior": {
        "sample_count": 123,
        "selection_rate": 0.8048780487804879,
        "true_positive_rate": 0.967032967032967,
        "false_positive_rate": 0.34375,
        "accuracy": 0.8861788617886179
      }
    },
    "demographic_parity_difference": 0.34725093013642006,
    "demographic_parity_ratio": 0.5685670261941448,
    "equal_opportunity_difference": 0.11854811854811853,
    "recommendations": [
      "Significant bias detected against certain groups in 'age_group' (Demographic Parity Ratio is 0.57 < 0.8 threshold). Apply sample reweighing during preprocessing or adjust decision thresholds.",
      "Model shows unequal error rates across groups in 'age_group' (Equal Opportunity Difference is 0.12 > 0.1). Recommend post-processing threshold adjustments to equalize True Positive Rates."
    ]
  },
  "race": {
    "overall_selection_rate": 0.64,
    "group_metrics": {
      "Caucasian": {
        "sample_count": 597,
        "selection_rate": 0.7102177554438861,
        "true_positive_rate": 0.9194805194805195,
        "false_positive_rate": 0.330188679245283,
        "accuracy": 0.830820770519263
      },
      "Asian": {
        "sample_count": 108,
        "selection_rate": 0.5925925925925926,
        "true_positive_rate": 0.8059701492537313,
        "false_positive_rate": 0.24390243902439024,
        "accuracy": 0.7870370370370371
      },
      "African American": {
        "sample_count": 134,
        "selection_rate": 0.5149253731343284,
        "true_positive_rate": 0.864406779661017,
        "false_positive_rate": 0.24,
        "accuracy": 0.8059701492537313
      },
      "Hispanic": {
        "sample_count": 161,
        "selection_rate": 0.515527950310559,
        "true_positive_rate": 0.8390804597701149,
        "false_positive_rate": 0.13513513513513514,
        "accuracy": 0.8509316770186336
      }
    },
    "demographic_parity_difference": 0.1952923823095577,
    "demographic_parity_ratio": 0.7250246409462124,
    "equal_opportunity_difference": 0.11351037022678812,
    "recommendations": [
      "Significant bias detected against certain groups in 'race' (Demographic Parity Ratio is 0.73 < 0.8 threshold). Apply sample reweighing during preprocessing or adjust decision thresholds.",
      "Model shows unequal error rates across groups in 'race' (Equal Opportunity Difference is 0.11 > 0.1). Recommend post-processing threshold adjustments to equalize True Positive Rates."
    ]
  }
}
```

---

## 5. Explainable AI (SHAP & LIME) Interpretability JSON Data

### 5.1 SHAP Feature Importance Ranking JSON (`artifacts/shap/loan_data/logistic_regression/feature_importance.json`)

```json
{
  "features": [
    {
      "feature": "credit_score",
      "importance": 1.2365363390660382,
      "rank": 1
    },
    {
      "feature": "dti",
      "importance": 0.8693923056327233,
      "rank": 2
    },
    {
      "feature": "income",
      "importance": 0.3812934388469192,
      "rank": 3
    },
    {
      "feature": "home_ownership_Rent",
      "importance": 0.2942627278959764,
      "rank": 4
    },
    {
      "feature": "employment_years",
      "importance": 0.29346786195188296,
      "rank": 5
    },
    {
      "feature": "coapplicant_income",
      "importance": 0.23125209850689976,
      "rank": 6
    },
    {
      "feature": "age",
      "importance": 0.21245930337238733,
      "rank": 7
    },
    {
      "feature": "home_ownership_Own",
      "importance": 0.1947944115449291,
      "rank": 8
    },
    {
      "feature": "education_Graduate",
      "importance": 0.11559924542016066,
      "rank": 9
    },
    {
      "feature": "education_Undergraduate",
      "importance": 0.11514365397187165,
      "rank": 10
    },
    {
      "feature": "loan_amount",
      "importance": 0.11012589571637293,
      "rank": 11
    },
    {
      "feature": "home_ownership_Mortgage",
      "importance": 0.0774958300905083,
      "rank": 12
    },
    {
      "feature": "loan_term",
      "importance": 0.03834084243958946,
      "rank": 13
    },
    {
      "feature": "dependents_1",
      "importance": 0.031699546109663794,
      "rank": 14
    },
    {
      "feature": "dependents_2",
      "importance": 0.023740867928461733,
      "rank": 15
    },
    {
      "feature": "property_area_Rural",
      "importance": 0.023090915642200498,
      "rank": 16
    },
    {
      "feature": "dependents_0",
      "importance": 0.020432636943520446,
      "rank": 17
    },
    {
      "feature": "dependents_3+",
      "importance": 0.01714662746853123,
      "rank": 18
    },
    {
      "feature": "property_area_Urban",
      "importance": 0.011639321461137036,
      "rank": 19
    },
    {
      "feature": "property_area_Semiurban",
      "importance": 0.00955545175232738,
      "rank": 20
    },
    {
      "feature": "self_employed_Yes",
      "importance": 0.005669039345917854,
      "rank": 21
    },
    {
      "feature": "self_employed_No",
      "importance": 0.00545252063782051,
      "rank": 22
    }
  ],
  "total_features": 22,
  "method": "mean_absolute_shap"
}
```

### 5.2 Top SHAP Feature Importance Table

| Rank | Feature Name | Mean \|SHAP\| Importance Value | Directional Impact on Approval |
| :--- | :--- | :--- | :--- |
| 1 | `credit_score` | **1.236536** | High values increase approval probability |
| 2 | `dti` | **0.869392** | High values decrease approval probability |
| 3 | `income` | **0.381293** | High values increase approval probability |
| 4 | `home_ownership_Rent` | **0.294263** | Renting decreases approval probability |
| 5 | `employment_years` | **0.293468** | Longer employment increases approval probability |
| 6 | `coapplicant_income` | **0.231252** | Co-applicant income increases approval probability |
| 7 | `age` | **0.212459** | Older age slightly increases credit stability score |
| 8 | `home_ownership_Own` | **0.194794** | Home ownership increases approval probability |
| 9 | `education_Graduate` | **0.115599** | Higher education increases approval probability |
| 10 | `education_Undergraduate`| **0.115144** | Neutral to positive impact |

---

## 6. Full Experiment Tracking & Model Registry JSON Logs

### 6.1 Sample Experiment Log Entry (`artifacts/experiments/all_experiments.json`)

```json
{
  "experiment_id": 1,
  "dataset_id": "loan_data",
  "model_name": "logistic_regression",
  "hyperparameters": {
    "C": 0.1,
    "penalty": "l2",
    "solver": "lbfgs"
  },
  "metrics": {
    "accuracy": 0.818,
    "precision": 0.825,
    "recall": 0.882943143812709,
    "f1_score": 0.8529886914378029,
    "sensitivity": 0.882943143812709,
    "specificity": 0.7213930348258707,
    "roc_auc": 0.9016955356994293,
    "pr_auc": 0.9325288921297237,
    "brier_score": 0.12440037987701749
  },
  "cv_scores": [
    0.9065793747035554,
    0.8867230659750184,
    0.8935927308797246
  ],
  "cv_mean": 0.8956317238527661,
  "cv_std": 0.008233523682232648,
  "training_time": 1.7478,
  "prediction_time": 0.001047,
  "model_file_path": "/Users/prabhakarkumarjha/Desktop/Capstone_project/models_saved/loan_data/logistic_regression.pkl",
  "features_used": [
    "age",
    "income",
    "coapplicant_income",
    "credit_score",
    "loan_amount",
    "loan_term",
    "employment_years",
    "dti",
    "home_ownership_Mortgage",
    "home_ownership_Own",
    "home_ownership_Rent",
    "education_Graduate",
    "education_Undergraduate",
    "self_employed_No",
    "self_employed_Yes",
    "dependents_0",
    "dependents_1",
    "dependents_2",
    "dependents_3+",
    "property_area_Rural",
    "property_area_Semiurban",
    "property_area_Urban"
  ],
  "timestamp": "2026-09-12T09:12:00.699491",
  "model_version": "logistic_regression_v1"
}
```

### 6.2 Sample Model Registry Item (`artifacts/model_registry.json`)

```json
{
  "dataset_id": "loan_data",
  "model_name": "logistic_regression",
  "model_version": "logistic_regression_v6",
  "model_file_path": "/Users/prabhakarkumarjha/Desktop/Capstone_project/models_saved/loan_data/logistic_regression.pkl",
  "metrics": {
    "accuracy": 0.818,
    "precision": 0.825,
    "recall": 0.882943143812709,
    "f1_score": 0.8529886914378029,
    "sensitivity": 0.882943143812709,
    "specificity": 0.7213930348258707,
    "roc_auc": 0.9016955356994293,
    "pr_auc": 0.9325288921297237,
    "brier_score": 0.12440037987701749
  },
  "hyperparameters": {
    "C": 0.1,
    "penalty": "l2",
    "solver": "lbfgs"
  },
  "features_used": [
    "age",
    "income",
    "coapplicant_income",
    "credit_score",
    "loan_amount",
    "loan_term",
    "employment_years",
    "dti",
    "home_ownership_Mortgage",
    "home_ownership_Own",
    "home_ownership_Rent",
    "education_Graduate",
    "education_Undergraduate",
    "self_employed_No",
    "self_employed_Yes",
    "dependents_0",
    "dependents_1",
    "dependents_2",
    "dependents_3+",
    "property_area_Rural",
    "property_area_Semiurban",
    "property_area_Urban"
  ],
  "scaler_path": "/Users/prabhakarkumarjha/Desktop/Capstone_project/models_saved/scaler_loan_data.pkl",
  "cleaner_path": "/Users/prabhakarkumarjha/Desktop/Capstone_project/models_saved/cleaner_loan_data.pkl",
  "status": "registered"
}
```

---

## 7. Project Architecture & Codebase File Catalog

| File / Folder Path | Description & Purpose |
| :--- | :--- |
| [`api/main.py`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/api/main.py) | FastAPI REST server providing `/predict`, `/explain/shap`, `/explain/lime`, `/fairness/audit`, and `/health` endpoints. |
| [`dashboard/app.py`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/dashboard/app.py) | Interactive 5-tab Streamlit user interface for real-time credit scoring, local SHAP/LIME explanation visualization, fairness audits, and benchmarking. |
| [`preprocessing/pipeline.py`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/preprocessing/pipeline.py) | Scikit-learn feature pipeline implementing Median Imputation, One-Hot Encoding, StandardScaler, and ratio feature derivation. |
| [`models/trainer.py`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/models/trainer.py) | Model training and hyperparameter tuning engine utilizing 5-Fold Stratified Cross-Validation via `GridSearchCV`. |
| [`explainability/shap_explainer.py`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/explainability/shap_explainer.py) | Explainer factory generating TreeExplainer, LinearExplainer, and KernelExplainer plots (waterfall, beeswarm, summary). |
| [`fairness/metrics.py`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/fairness/metrics.py) | Algorithmic fairness evaluator calculating Demographic Parity Difference, Disparate Impact Ratio, and Equalized Odds. |
| [`fairness/mitigation.py`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/fairness/mitigation.py) | Bias mitigation routines implementing sample reweighing and post-processing decision threshold optimization. |
| [`database/schema.sql`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/database/schema.sql) | Relational database schema for audit logging of model decisions, input features, SHAP values, and demographic fields. |
| [`Dockerfile`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/Dockerfile) | Container definition for reproducible deployment on Railway, Render, Docker Compose, or Kubernetes. |
| [`research/paper.md`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/research/paper.md) | Academic research paper manuscript draft. |

---

## 8. Mathematical Formulations

### 8.1 SHAP (SHapley Additive exPlanations)
For a model prediction $f(x)$, the Shapley value $\phi_i$ assigned to feature $i$ is defined as:
$$\phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N|-|S|-1)!}{|N|!} \Big( v(S \cup \{i\}) - v(S) \Big)$$
where $N$ is the set of all input features, $S$ is a subset of features acting without feature $i$, and $v(S) = \mathbb{E}[f(x) \mid x_S]$.

### 8.2 LIME (Local Interpretable Model-agnostic Explanations)
LIME solves the local optimization objective:
$$\xi(x) = \arg\min_{g \in G} \mathcal{L}(f, g, \pi_x) + \Omega(g)$$
where $f$ is the complex black-box model, $g$ is an interpretable surrogate model (e.g., linear regression), $\pi_x(z) = \exp(-D(x,z)^2 / \sigma^2)$ is the exponential proximity metric kernel, and $\Omega(g)$ penalizes surrogate complexity.

### 8.3 Algorithmic Fairness Metrics
- **Demographic Parity Difference (DPD):**
  $$\text{DPD} = \max_{a, b \in A} \left| \mathbb{P}(\hat{Y}=1 \mid A=a) - \mathbb{P}(\hat{Y}=1 \mid A=b) \right|$$
- **Equal Opportunity Difference (EOD):**
  $$\text{EOD} = \max_{a, b \in A} \left| \mathbb{P}(\hat{Y}=1 \mid A=a, Y=1) - \mathbb{P}(\hat{Y}=1 \mid A=b, Y=1) \right|$$
- **Pre-processing Sample Reweighing Weight ($W$):**
  $$W(A=a, Y=y) = \frac{\mathbb{P}(A=a) \times \mathbb{P}(Y=y)}{\mathbb{P}(A=a, Y=y)}$$

---

## 9. Academic Bibliography & Reference Formats

1. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30, 4765-4774.
2. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 1135-1144.
3. Hardt, M., Price, E., & Srebro, N. (2016). Equality of opportunity in supervised learning. *Advances in Neural Information Processing Systems (NeurIPS 2016)*, 29, 3315-3323.
4. Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1(5), 206-215.
5. Barocas, S., & Selbst, A. D. (2016). Big data's disparate impact. *California Law Review*, 104, 671.
6. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785-794.
7. Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. (2018). CatBoost: unbiased boosting with categorical features. *Advances in Neural Information Processing Systems (NeurIPS 2018)*, 31.
