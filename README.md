This project was used for the paper : Characterizing the usage of CI tools in ML projects

Link to preprint: https://dhiarzig.netlify.app/publication/characterizing-the-usage-of-ci-tools-in-ml-projects/

@inproceedings{10.1145/3544902.3546237,
author = {Rzig, Dhia Elhaq and Hassan, Foyzul and Bansal, Chetan and Nagappan, Nachiappan},
title = {Characterizing the Usage of CI Tools in ML Projects},
year = {2022},
isbn = {9781450394277},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3544902.3546237},
doi = {10.1145/3544902.3546237},
abstract = {Background: Continuous Integration (CI) has become widely adopted to enable faster code change integration. Meanwhile, Machine Learning (ML) is being used by software applications for previously unsolvable real-world scenarios. ML projects employ development processes different from those of traditional software projects, but they too require multiple iterations in their development, and may benefit from CI. Aims: While there are many works covering CI within traditional software, none of them empirically explored the adoption of CI and its associated issues within ML projects. To address this knowledge gap, we performed an empirical analysis comparing CI adoption between ML and Non-ML projects. Method: We developed TraVanalyzer, the first Travis CI configuration analyzer, to analyze the CI practices of ML projects, and developed a CI log analyzer to identify the different CI problems of ML projects. Results: We found that Travis CI is the most popular CI tool for ML projects, and that their CI adoption lags behind that of Non-ML projects, but that ML projects which adopted CI, used it for building, testing, code analysis, and automatic deployment more than Non-ML projects. Furthermore, while CI in ML projects is as likely to experience problems as CI in Non-ML projects, it has more varied reasons for build-breakage. The most frequent CI failures of ML projects are due to testing-related problems, similar to Non-ML and OSS CI failures. Conclusion: To the best of our knowledge, this is the first work that has analyzed ML projects’ CI usage, practices, and issues, and contextualized its results by comparing them with similar Non-ML projects. It provides findings for researchers and ML developers to identify possible improvement scopes for CI in ML projects.},
booktitle = {Proceedings of the 16th ACM / IEEE International Symposium on Empirical Software Engineering and Measurement},
pages = {69–79},
numpages = {11},
location = {Helsinki, Finland},
series = {ESEM '22}
}
