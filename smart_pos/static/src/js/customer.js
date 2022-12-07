app.controller("customerCtr", ['$scope', '$rootScope', '$http', '$filter', function($scope, $rootScope, $http, $filter) {

    let pos_counter = localStorage.getItem('pos_counter')
    pos_counter = JSON.parse(pos_counter)
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

    // Tao o trong api
    // $rootScope.info_customer.creater_customer = pos_counter["seller"]["seller_name"]

    $scope.getAddress = () => {
        $http({
            method: "POST",
            url: "/api/area",
            params: $scope.paramArea,
        }).then(function mySuccess(res) {
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

    $rootScope.createCustomer = () => {
        if (!$rootScope.info_customer.name || $rootScope.info_customer.name && $rootScope.info_customer.name.length < 1) {
            return toastr.error('Tên khách hàng là bắt buộc')
        } else {
            console.log($rootScope.info_customer)
            if ($rootScope.info_customer.birthday) {
                $rootScope.info_customer.birthday = new Date($rootScope.info_customer.birthday)
                $rootScope.info_customer.birthday = $filter('date')($rootScope.info_customer.birthday, "dd/MM/yyyy")

            }
            $http({
                method: "POST",
                url: "/api/customer",
                params: $rootScope.info_customer,
            }).then(function mySuccess(response) {
                $rootScope.getCustomer()
                $rootScope.customerClicked($rootScope.info_customer)
                $rootScope.info_customer = {}
                return toastr.success(response.data.message);
            }, function myError(response) {});
        }
    }
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
        $scope.provinceAutoHide = false
        $scope.districtAutoHide = false
        $scope.wardAutoHide = false
        if (e.is_province) {
            $rootScope.info_customer.province = e.id
            $rootScope.info_customer.province_name = e.name
            $scope.paramArea = { 'province_id': e.code_province }
        } else if (e.is_district) {
            $rootScope.info_customer.district = e.id
            $rootScope.info_customer.district_name = e.name
            $scope.paramArea = { 'district_id': e.code_district }
        } else if (e.is_ward) {
            $rootScope.info_customer.ward_name = e.name
            $rootScope.info_customer.ward = e.id
        }
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