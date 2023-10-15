## 2023-2학기 스마트농업프로그래밍에서 진행한 복숭아 개화시기 예측모델입니다. 

### 복숭화 개화 모델 종류

- 본 프로그램에서 사용한 복숭아 개화 모델은 CD 모델(Chill day model)과 DVR 모델(Development Rate model) 두개 입니다.
        
- CD 모델은 일의 최고 및 최저기온을 이용해 기준온도(threshold temperature, Tc)로부터 유효한 온도범위에 따라 가중치를 달리하 여 내생휴면해제 이전까지는 냉각량(chill unit), 그 이 후는 가온량(heat unit)으로 표현하여 
고온 요구도를 넘는 날을 기점으로 만개기로 간주합니다.
        
- DVR 모델은 온도에 따른 과수의 발육 속도를 계산하여 적산함으로써 만개기를 예측하는 모델입니다. 여기서 온도는 5°C 이상의 평균 기온을 기록한 날만 반영합니다.
        
        
![image](https://github.com/EthanSeok/APSIM_Wheat_Scenario/assets/93086581/59a79943-e682-4278-8b76-f6e38db32158)

![image](https://github.com/EthanSeok/APSIM_Wheat_Scenario/assets/93086581/8d042ecb-7c18-4f5b-abb6-3add02904dba)
        
        
### 참고 문헌

- Chun, J. A., Kang, K., Kim, D., Han, H. H., & Son, I. C. (2017). Prediction of full blooming dates of five peach cultivars (Prunus persica) using temperature-based models. Scientia Horticulturae, 220, 250-258.
