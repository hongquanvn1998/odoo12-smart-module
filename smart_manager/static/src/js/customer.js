app.controller("customerCtr", ['$scope', '$rootScope', '$http', '$filter', function($scope, $rootScope, $http, $filter) {

    $scope.provinceAutoHide = false
    $scope.districtAutoHide = false
    $scope.wardAutoHide = false
    $rootScope.info_customer = {}
    $scope.paramArea = {}
    $scope.provinceList = []
    $scope.districtList = []
    $scope.wardList = []
    $rootScope.info_customer.province = null
    $rootScope.info_customer.district = null
    $rootScope.info_customer.ward = null

    $scope.getAddress = () => {
        $http({
            method: "POST",
            url: "/api/area-register",
            params: $scope.paramArea,
        }).then(function mySuccess(res) {
            console.log(res)
            if (res.data.province && res.data.province.length > 0) {
                $scope.provinceList = res.data.province
            } else if (res.data.district && res.data.district.length > 0) {
                $scope.districtList = res.data.district
            } else {
                $scope.wardList = res.data.ward
            }
        }, function myError() {})
    }
    $scope.getAddress()

    $scope.onSearchArea = () => {
        if ($rootScope.info_customer.province_name && $rootScope.info_customer.province_name.length > 0 && $("#province-input").is(":focus")) {
            $scope.provinceAutoHide = true
            $scope.districtAutoHide = false
            $scope.wardAutoHide = false
        } else if ($rootScope.info_customer.district_name && $rootScope.info_customer.district_name.length > 0 && $("#district-input").is(":focus")) {
            $scope.districtAutoHide = true
            $scope.provinceAutoHide = false
            $scope.wardAutoHide = false
        } else if ($rootScope.info_customer.ward_name && $rootScope.info_customer.ward_name.length > 0 && $("#ward-input").is(":focus")) {
            $scope.wardAutoHide = true
            $scope.provinceAutoHide = false
            $scope.districtAutoHide = false
        }
    }
    $scope.selectArea = (e) => {
        var form = localStorage.getItem('form_register')
        form = JSON.parse(form)
        $scope.provinceAutoHide = false
        $scope.districtAutoHide = false
        $scope.wardAutoHide = false
        if (e.is_province) {
            $rootScope.registerData.province = e.id
            $rootScope.registerData.province_name = e.name
            $rootScope.info_customer.province_name = e.name
            $scope.paramArea = { 'province_id': e.code_province }
        } else if (e.is_district) {
            $rootScope.registerData.district = e.id
            $rootScope.registerData.district_name = e.name
            $rootScope.info_customer.district_name = e.name
            $scope.paramArea = { 'district_id': e.code_district }
        } else if (e.is_ward) {
            $rootScope.info_customer.ward_name = e.name
            $rootScope.registerData.ward_name = e.name
            $rootScope.registerData.ward = e.id
        }
        form = $rootScope.registerData

        $scope.getAddress()
    }
    $(document).mouseup(function(e) {
        if (!$("#province-input").is(e.target) && $("#province-input").has(e.target).length === 0) {
            $scope.provinceAutoHide = false
        }
        if (!$("#district-input").is(e.target) && $("#district-input").has(e.target).length === 0) {
            $scope.districtAutoHide = false
        }
        if (!$("#ward-input").is(e.target) && $("#ward-input").has(e.target).length === 0) {
            $scope.wardAutoHide = false
        }
    });
}])