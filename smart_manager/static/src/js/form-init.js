var app = angular.module("appRegister", []);

app.controller("registerCtrl", ['$scope', '$rootScope', '$timeout', '$http','$interval','$window', function($scope, $rootScope, $timeout, $http,$interval,$window) {
    // var tick = () => {
    //     $scope.clock = Date.now();
    // }
    // tick();
    // $interval(tick, 1000);
    $rootScope.appModules = []
    $scope.countApps = []
    $rootScope.loadedPayment = false;

    $timeout(function() {
        $rootScope.loadedPayment = true;
    }, 300);

    $rootScope.showTab = (n) => {
        var x = $(".tab");
        var y = $(".step");
       
        x[n].style.display = "block";
        if (n == 0) {
            $("#prevBtn").removeAttr("style").hide();
            $("#nextBtn").removeAttr("style").hide();
        } else {
            $("#prevBtn").show()
            $("#nextBtn").show()
        }
        if (n == (x.length - 1)) {
            $("#nextBtn").removeAttr("style").hide();
            $("#SubmitBtn").show()
        } else {
            $("#SubmitBtn").removeAttr("style").hide();
        }
         
        // step-active , validate-input
        if(n == 0){
          y.removeClass(" active bg-success");
          y.eq(0).addClass(" active bg-success");
        } else if( n == 1){
          y.removeClass("active bg-success");
          y.eq(1).addClass(" active bg-success");
        } else {
          y.removeClass("active bg-success");
          y.eq(2).addClass(" active bg-success");
        }

        
      }

    $rootScope.btnEvent = (n) => {
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        var x = $(".tab");
        x[$rootScope.registerData.currentTab].style.display = "none";
        $rootScope.registerData.currentTab = $rootScope.registerData.currentTab + n;
        form = $rootScope.registerData
        localStorage.setItem('form_register', JSON.stringify(form))
        $rootScope.showTab($rootScope.registerData.currentTab)
    }

    $rootScope.nextTab = () => {
        $rootScope.btnEvent(1);
    }

    $rootScope.preTab = () => {
        $rootScope.btnEvent(-1);
    }

    const initFunc = ()=>{
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        // var appModules = localStorage.getItem('app_modules')
        // appModules = JSON.parse(appModules)
        $rootScope.registerData = {
            currentTab:0,
            isAnnualy: false,
            paymentPeriods: 0,
            businessCategoryId: 0,
            appModules: [],
            appPrice:[],
            partnerName:'',
            mobile:'',
            email:'',
            useType: 'trial',
            province_name:'',
            district_name:'',
            ward_name:'',
            businessTaxCode:'',
            shopDomain:'',
            username:'',
            password:'',
            businessType:'',
            inValid:false,
            whiteSpace:false,
            businessSize:0,
            province:1,
            district:1,
            ward:1,
        }
        if(!form || form && form.length <1){
            localStorage.setItem('form_register', JSON.stringify($rootScope.registerData))
            $rootScope.showTab($rootScope.registerData.currentTab)
            return $rootScope.registerData
        }
        $rootScope.showTab(form.currentTab)
        $rootScope.registerData = form
        console.log('initFunc',$rootScope.registerData)
        return $rootScope.registerData
    }

    $scope.businessSize = [{
        name: '<10',
        value: 0
    }, {
        name: '10-30',
        value: 1
    }, {
        name: '31-50',
        value: 2
    }, {
        name: '51-100',
        value: 3
    }, {
        name: '101-200',
        value: 4
    }, {
        name: '>200',
        value: 5
    }];
    
    $scope.title = "Form dang ky ung dung";
    $rootScope.getBusinessCategory = () => {
        $rootScope.businessCategory = [];
        $http({
            method: "POST",
            url:'/api/business-category',
        }).then(function mySuccess(response) {
            $rootScope.businessCategory  = response.data
        }, function myError(response) {
            console.log('error category-business',response)
        })
    }

    $scope.nextTopApp = (formRegister) => {
        var format = /[ `!@#$%^&*()+\-=\[\]{};':"\\|,.<>\/?~]/;
        var unicode = /[^\u0000-\u007f]/
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        if(formRegister && formRegister.$valid){
            $http({
                method: "POST",
                url:'/api/check-exist-database',
                params:{'shopDomain':$rootScope.registerData.shopDomain}
            }).then(function mySuccess(response) {
                console.log('getAppModules',$rootScope.registerData)
                if(response.data.success){
                    if ($rootScope.registerData.shopDomain.indexOf(' ') >= 0 || format.test($rootScope.registerData.shopDomain) || unicode.test($rootScope.registerData.shopDomain)) {
                        $rootScope.registerData.whiteSpace = true
                    }else{
                        $scope.getAppModules()
                        $rootScope.registerData.whiteSpace = false
                        $rootScope.registerData.inValid = false
                        localStorage.setItem('form_register', JSON.stringify(form))
                        $rootScope.nextTab()
                    }
                }else{
                    toastr.error(`Tên miền ${$rootScope.registerData.shopDomain}.smarterp.vn đã tồn tại, vui lòng thay đổi tên miền của shop!`);
                    $rootScope.registerData.inValid = true
                }
            }, function myError(response) {
                console.log('error app-module',response)
            })
            
        }else{
            toastr.error("Vui lòng nhập đầy đủ thông tin" );
            $rootScope.registerData.inValid = true
        }
        form = $rootScope.registerData
        localStorage.setItem('form_register', JSON.stringify(form))
        return $rootScope.registerData
    }

    $scope.changeBusinessSize = ()=>{
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        form = $rootScope.registerData
        localStorage.setItem('form_register', JSON.stringify(form))
        return $rootScope.registerData
    }

    $scope.getAppModules = () => {
        $http({
            method: "POST",
            url:'/api/app-modules',
            params:{'id_period':$rootScope.registerData.paymentPeriods}
        }).then(function mySuccess(response) {
            var form = localStorage.getItem('form_register')
            form = JSON.parse(form)
            $rootScope.appModules  = response.data
            // if ($rootScope.registerData.appPrice.length > 0) {
                $rootScope.registerData.appModules.forEach(e => {
                    if ($rootScope.appModules[`${e}`]) {
                        $rootScope.appModules[`${e}`].checked = true
                    }
                });
            // }
            form = $rootScope.registerData
            localStorage.setItem('form_register', JSON.stringify(form))
            console.log('getAppModules',$rootScope.registerData)


        }, function myError(response) {
            console.log('error app-module',response)
        })
    }

    $rootScope.getPaymentPeriods = () => {
        $rootScope.listPaymentPeriods = [];
        $http({
            method: "POST",
            url:'/api/payment-period',
        }).then(function mySuccess(response) {
            var form = localStorage.getItem('form_register')
            form = JSON.parse(form)
            $rootScope.listPaymentPeriods = response.data
            if($rootScope.registerData.paymentPeriods == 0){
                let max = 0
                let paymentPeriodsTemporary = 0
                if($rootScope.registerData.isAnnualy){
                    max = $rootScope.listPaymentPeriods.annualy[0].value
                    paymentPeriodsTemporary = $rootScope.listPaymentPeriods.annualy[0].id
                    $rootScope.listPaymentPeriods.annualy.forEach(e => {
                        paymentPeriodsTemporary = e.value > max ? e.id : paymentPeriodsTemporary
                        max = e.value > max ? e.value : max
                    });
                }else{
                    max = $rootScope.listPaymentPeriods.monthly[0].value
                    paymentPeriodsTemporary = $rootScope.listPaymentPeriods.monthly[0].id
                    $rootScope.listPaymentPeriods.monthly.forEach(e => {
                        paymentPeriodsTemporary = e.value > max ? e.id : paymentPeriodsTemporary
                        max = e.value > max ? e.value  : max
                    });
                }
                $rootScope.registerData.paymentPeriods = paymentPeriodsTemporary
            }
            form = $rootScope.registerData
            localStorage.setItem('form_register', JSON.stringify(form))
            console.log('getPaymentPeriods',$rootScope.registerData)
            $scope.getAppModules()

        }, function myError(response) {
            console.log('error payment-period',response)
        })
    }

    $scope.changeTime = (time) => {
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        $rootScope.registerData.paymentPeriods = 0
        if(time == 0){
            $rootScope.registerData.isAnnualy = false;
        } else {
            $rootScope.registerData.isAnnualy = true;
        }
        $rootScope.registerData.appModules = []
        $rootScope.registerData.appPrice = []
        $rootScope.getPaymentPeriods()
        form = $rootScope.registerData
        localStorage.setItem('form_register', JSON.stringify(form))
    }
    
    $scope.addProduct = (model) =>{
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        if (model.checked == false) {
            var list_apps = []
            if(model.dependApps.length > 0){
                angular.forEach($rootScope.appModules,(e,k)=>{
                    if(e.checked == true){
                        list_apps= list_apps.concat(e.dependApps) 
                    }
                })
                $rootScope.registerData.appModules.splice($rootScope.registerData.appModules.indexOf(model.appId),1)
                $rootScope.registerData.appPrice.splice($rootScope.registerData.appPrice.indexOf(model.id),1)
                model.dependApps.forEach(e =>{
                    if(list_apps.indexOf(e) > -1){
                        if ($rootScope.appModules[`${e}`]) {
                            $rootScope.appModules[`${e}`].checked = true
                        }
                    }else{
                        if ($rootScope.appModules[`${e}`]) {
                            $rootScope.appModules[`${e}`].checked = false
                            $rootScope.registerData.appModules.splice($rootScope.registerData.appModules.indexOf(e),1)
                            $rootScope.registerData.appPrice.splice($rootScope.registerData.appPrice.indexOf($rootScope.appModules[`${e}`].id),1)
                        }
                    }
                })
            }else{
                var checkFlag = false
                angular.forEach($rootScope.appModules,(e,k)=>{
                    if(e.checked == true && e.dependApps.indexOf(model.appId) > -1){
                        checkFlag = true
                        toastr.error(`${model.appName} là bắt buộc `);
                    }
                })
                if (!checkFlag) {
                    $rootScope.registerData.appModules.splice($rootScope.registerData.appModules.indexOf(model.appId),1)
                    $rootScope.registerData.appPrice.splice($rootScope.registerData.appPrice.indexOf(model.id),1)
                }
                model.checked = !checkFlag ? false : true 
            }
        } else {
            model.dependApps.forEach(e => {
                if ($rootScope.appModules[`${e}`]) {
                    $rootScope.appModules[`${e}`].checked = true
                        
                    if($rootScope.registerData.appModules.indexOf($rootScope.appModules[`${e}`].appId) < 0 && $rootScope.registerData.appPrice.indexOf($rootScope.appModules[`${e}`].id) < 0){
                        $rootScope.registerData.appModules.push($rootScope.appModules[`${e}`].appId)
                        $rootScope.registerData.appPrice.push($rootScope.appModules[`${e}`].id)
                    }
                }

            });
            if($rootScope.registerData.appModules.indexOf(model.appId) < 0 && $rootScope.registerData.appPrice.indexOf(model.id) < 0){
                $rootScope.registerData.appModules.push(model.appId)
                $rootScope.registerData.appPrice.push(model.id)
            }
        }
        form = $rootScope.registerData
        localStorage.setItem('form_register', JSON.stringify(form))
    }

    $scope.businessCategorySelect = (id)=>{
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        $rootScope.registerData.businessCategoryId = id
        form = $rootScope.registerData
        localStorage.setItem('form_register', JSON.stringify(form))
        $rootScope.btnEvent(1)
    }

    $scope.submitButton = ()=>{
        $rootScope.loadedPayment = false;
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        if($rootScope.registerData.appPrice.length<1){
            toastr.error('Bạn chưa chọn sản phẩm')
        }else{
            $http({
                method:'POST',
                url:'/api/submit-register-form',
                data: JSON.stringify({
                    "jsonrpc": "2.0",
                    "params": {
                        form
                    },
                })
                // params:JSON.stringify($rootScope.registerData),
            }).then( function mySuccess(response){
                $rootScope.loadedPayment = true;
                var success = response.data
                toastr.success('Đăng ký thành công')
                // $window.location.href = 'http://www.google.com';
            },function myError(response) {
                toastr.error(response)
                console.log(response)
            }
            )
        }
    }


  
    initFunc()
    $rootScope.getPaymentPeriods();
    $rootScope.getBusinessCategory();

    // setTimeout(initFunc, 800)



}]);

app.filter('checked', () => {
    return function(input) {
        var out = {};
        angular.forEach(input,(e,k)=>{
            if(e.checked){
                out[k] = e
            }
        })
        return out;
    }
});

app.filter('sumOfValue', () => {
        return function (data) {        
            if (angular.isUndefined(data))
                return 0;        
            var sum = 0;        
            angular.forEach(data,function(value,key){
                if(value.checked){
                    sum = sum + parseInt(value.basePrice, 10);
                }
            });        
            return sum;
        }
    })