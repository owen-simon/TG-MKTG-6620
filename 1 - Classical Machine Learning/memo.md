# Memo

**To:** Devon Achebe, VP of Customer Retention at Summit Telecom<br>
**From:** Owen Simon<br>
**Subject:** Customer Churn Prediction Model

I developed a prediction model that can identify a more useful contact list than the current contract rule. After validating and testing on unseen data, two models identified top-20% contact lists with an observed churn rate of 69.40%, compared to the 39.86% observed churn rate of the current contract rule. While both models performed well, I recommend that Summit Telecom proceed with the boosted trees model, as it achieved a slightly higher final-test AUC of 0.8497.

The boosted trees model does not estimate whether contacting a customer will prevent them from churning. A key limitation of the analysis is that the retention campaign must achieve a save rate greater than 13.54% to generate positive net value. A 20% save rate would result in an estimated net value of $2,960.14 per 1,000 customers contacted, while a 10% save rate would result in a net loss of $1,619.93 per 1,000 customers contacted. If a pilot study indicates that less than 13.54% of otherwise-churning customers are persuaded to stay because of the contact, I would reconsider whether the retention campaign can generate enough value to justify its cost.