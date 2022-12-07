app.controller('orderInfoCtrl', ['$scope', '$rootScope', '$http', '$interval', '$filter', '$window', function($scope, $rootScope, $http, $interval, $filter, $window) {
    var tick = () => {
        $scope.clock = Date.now();
    }
    tick();
    $interval(tick, 1000);

    $scope.$window = $window;
    $rootScope.openSearchCustomer = false;
    // $scope.searchCustomer = ""
    $scope.showSearch = function() {
        $scope.searchCustomer = angular.element(document.querySelector('#customerSearchInput')).val()
        if ($scope.searchCustomer && $scope.searchCustomer.length > 0) {
            return $rootScope.openSearchCustomer = true
        }
        return $rootScope.openSearchCustomer = false
    }
    $(document).mouseup(function(e) {
        var container = $("#customerSearchInput")
        if (!container.is(e.target) && container.has(e.target).length === 0) {
            $rootScope.openSearchCustomer = false
        }
    });

    $(document).on('keydown', function(event) {
        if (event.which == 114 && event.target.id != 'productSearchInput') {
            $rootScope.openSearchCustomer = false
            $rootScope.productAutoHide = false
            if ($("#productSearchInput").hasClass('ng-hide')) {
                setTimeout(function() {
                    $("#productSearchQrInput").focus().select();
                }, 300)
            } else {
                setTimeout(function() {
                    $("#productSearchInput").focus().select();
                }, 300)
            }

            return false
        }
        if (event.which == 115 && event.target.id != 'customerSearchInput') {
            $rootScope.productAutoHide = false
            $rootScope.openSearchCustomer = false
            setTimeout(function() {
                $("#customerSearchInput").focus().select();
            }, 300);

        }
        if (event.which == 119 && event.target.id != 'click-payment-method') {
            $rootScope.openSearchCustomer = false
            $rootScope.productAutoHide = false
            setTimeout(function() {
                $("#paying-amount-input").focus().select();
            }, 300);

        }
        if (event.which == 112 && event.target.id != 'productSearchInput') {
            $rootScope.openSearchCustomer = false
            $rootScope.productAutoHide = false
            $("#create-tab-button").trigger('click')
            return false
        }
        if (event.which == 117 && event.target.id != 'productSearchInput') {
            $rootScope.openSearchCustomer = false
            $rootScope.productAutoHide = false
            $("#change-sale-mode-button").trigger('click')
            return false
        }
        if (event.which == 113 && event.target.id != 'productSearchInput') {
            $rootScope.openSearchCustomer = false
            $rootScope.productAutoHide = false
            $("#change-qr-mode-button").trigger('click')
            return false
        }
        if (event.which == 120 && event.target.id != 'productSearchInput') {
            $rootScope.openSearchCustomer = false
            $rootScope.productAutoHide = false
            $("#saveTransaction").trigger('click')
            return false
        }

        if (event.which == 118 && event.target.id != 'productSearchInput') {
            $rootScope.openSearchCustomer = false
            $rootScope.productAutoHide = false
            $("#printPaperForm").trigger('click')
            return false
        }

    });

    let arr_customer = {}
    $rootScope.getCustomer = () => {
        $http({
            method: "POST",
            url: "/api/customer",
        }).then(function mySuccess(response) {
            $rootScope.list_customer = response.data.customer
        }, function myError(response) {
            // console.log(response)
        });
    }
    $rootScope.getCustomer()
    $scope.isShowPointMethod = true
    $scope.pointToMoney = 0
    $rootScope.customerClicked = (prod) => {
        let orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        let pos_counter = localStorage.getItem('pos_counter')
        pos_counter = JSON.parse(pos_counter)
        config_settings = pos_counter["config_settings"]
        customer = {
            'isDeleted': false,
        }
        prod["pointToMoney"] = Math.ceil(prod.prp_points * config_settings.reward_point_money_to_point / config_settings.reward_point_point_to_money)
        $rootScope.list_customer.forEach((e) => {
            if (prod.id == e.id) {
                orders[$rootScope.currentIndex].currentCustomer = prod
            }
        })
        $rootScope.currentCustomer = orders[$rootScope.currentIndex].currentCustomer
        localStorage.setItem('pos_orders', JSON.stringify(orders))
    }

    $scope.openEditForm = () => {
        let orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        $rootScope.info_customer = orders[$rootScope.currentIndex].currentCustomer
        if ($rootScope.info_customer.birthday && $rootScope.info_customer.birthday.length > 0) {
            $rootScope.info_customer.birthday = new Date(orders[$rootScope.currentIndex].currentCustomer.birthday)
        }
    }

    $scope.changeCustomer = () => {
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        delete $rootScope.currentCustomer
        $rootScope.info_customer = {}
        delete orders[session_selected.sessionIndex].currentCustomer
        localStorage.setItem('pos_orders', JSON.stringify(orders))
        $scope.searchCustomer = ""
        setTimeout(function() {
            $("#customerSearchInput").focus().select();
        }, 300);
    }

    $scope.paymentMethods = []
    $scope.payments = []
    $rootScope.isHidePaymentButton = false
    $scope.payingAmountSuggestion = () => {

        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        var paying = orders[session_selected.sessionIndex].customerPay;
        paying = $scope.currentAmount;

        denominations = [5000, 10000, 20000]
        unit = [1000, 2000, 5000]
        hundredsofthousands = [100000, 200000, 300000, 500000]
        $scope.listSuggest = []
        $scope.suggestAmount = 0
        if (paying < 500000) {
            if (paying <= 50000) {
                if (paying % 5000 == 0) {
                    $scope.listSuggest.push(paying)
                    switch (paying) {
                        case paying < 10000:
                            $scope.listSuggest.push(10000, 20000, 50000)
                            break;
                        case 10000 < paying < 20000:
                            $scope.listSuggest.push(20000, 50000)
                            break;
                        case 20000 < paying < 30000:
                            $scope.listSuggest.push(30000, 50000)
                            break;
                        case 30000 < paying < 40000:
                            $scope.listSuggest.push(40000)
                            break;
                        case 40000 < paying < 50000:
                            $scope.listSuggest.push(50000)
                            break;
                        default:
                            break;
                    }
                } else if (paying % 5000 != 0) {
                    suggestAmount = Math.floor(paying / 5000) * 5000
                    $scope.listSuggest = unit.map(x => x + suggestAmount).filter(xx => xx > paying)
                    switch (paying) {
                        case paying < 10000:
                            $scope.listSuggest.push(10000, 20000, 50000)
                            break;
                        case 10000 < paying < 20000:
                            $scope.listSuggest.push(20000, 50000)
                            break;
                        case 20000 < paying < 30000:
                            $scope.listSuggest.push(30000, 50000)
                            break;
                        case 30000 < paying < 40000:
                            $scope.listSuggest.push(40000)
                            break;
                        case 40000 < paying < 50000:
                            $scope.listSuggest.push(50000)
                            break;
                        default:
                            break;
                    }
                }
                $scope.listSuggest.push(50000, 100000, 200000, 500000)
            } else if (50000 < paying && paying <= 100000) {
                suggestAmount = (Math.floor(paying / 10000) * 10000)
                $scope.listSuggest = denominations.map(x => x + suggestAmount).filter(xx => xx > paying)
                $scope.listSuggest.push(100000, 200000, 300000, 500000)
                $scope.listSuggest = $scope.listSuggest.filter((v, i) => $scope.listSuggest.indexOf(v) === i)
            } else if (100000 < paying && paying <= 500000) {
                suggestAmount = (Math.floor(paying / 10000) * 10000)
                $scope.listSuggest = denominations.map(x => x + suggestAmount).filter(xx => xx > paying)
                maxListSuggest = Math.max(...$scope.listSuggest)
                $scope.listSuggest = hundredsofthousands.filter((x => x > maxListSuggest)).concat($scope.listSuggest)
                $scope.listSuggest = $scope.listSuggest.filter((v, i) => $scope.listSuggest.indexOf(v) === i)
            }
        } else if (paying > 500000) {
            banknoteNumber = Math.floor(paying / 500000)
            suggestAmount1 = banknoteNumber * 500000 + 100000
            suggestAmount2 = banknoteNumber * 500000 + 200000
            suggestAmount5 = banknoteNumber * 500000 + 500000
            $scope.listSuggest.push(suggestAmount1, suggestAmount5, suggestAmount2)
            for (i = 0; i < $scope.listSuggest.length; i++) {
                if ($scope.listSuggest[i] < paying) {
                    $scope.listSuggest.splice(i, 1)
                }
            }
        }
        $scope.listSuggest.push(paying)
        $scope.listSuggest = $scope.listSuggest.filter((v, i) => $scope.listSuggest.indexOf(v) === i)
        $scope.listSuggest.sort(function(a, b) {
            return a - b
        })
        return $scope.listSuggest
    };

    $scope.checkPaymentPoint = () => {
        let pos_counter = localStorage.getItem('pos_counter')
        pos_counter = JSON.parse(pos_counter)
        checkMP = pos_counter["config_settings"].reward_point_is_point_to_money

    }
    $scope.listSuggest = []
    $scope.openEditPayingForm = () => {
        let orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        let session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        if (orders[session_selected.sessionIndex].CurrentPayments && orders[session_selected.sessionIndex].CurrentPayments.length > 0) {
            $scope.currentAmount = orders[session_selected.sessionIndex].customerPay - orders[session_selected.sessionIndex].payingAmount
        } else {
            $scope.currentAmount = orders[session_selected.sessionIndex].customerPay
        }

        if ($scope.currentAmount <= 0) {
            $scope.currentAmount = 0
            $rootScope.isHidePaymentButton = true
        } else {
            $rootScope.isHidePaymentButton = false
        }
        $rootScope.customerPay_present = orders[session_selected.sessionIndex].payingAmount
        $scope.payments = orders[session_selected.sessionIndex].CurrentPayments
        $scope.amount_before = $scope.currentAmount
        $scope.amount_present = $scope.currentAmount
            // $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
        $scope.payingAmountSuggestion()
        $scope.checkPaymentPoint()
        $rootScope.switchSuggest()

    }


    $rootScope.bankAccounts = []
    $http.get("/api/bank-account").then(
        function(response) {
            $rootScope.bankAccounts = response.data;
        },
        function Error(response) {}
    );
    $scope.payment = {}
    $scope.getPaymentMethod = () => {
        let pos_counter = localStorage.getItem('pos_counter')
        pos_counter = JSON.parse(pos_counter)
        checkMP = pos_counter["config_settings"].reward_point_is_point_to_money
        let AllPaymentMethods = localStorage.getItem('pos_counter')
        AllPaymentMethods = JSON.parse(AllPaymentMethods)
        AllPaymentMethods.payment_method.forEach((e) => {
            $scope.payment[`${e.payment_code}`] = {
                Method: e.payment_code,
                MethodStr: e.payment_name,
                Amount: 0,
                Id: e.payment_id,
                AccountId: null,
                payment_type: e.payment_type,
                bankAccounts: e.payment_journal.length > 0 ? e.payment_journal : null,
            }
        })
        if (!checkMP) {
            angular.forEach($scope.payment, (e, i) => {
                if (e.payment_type == 'point') {
                    delete $scope.payment[i]
                    $scope.isShowPointMethod = false
                }
            });
        }
    }

    $scope.updatePayments = (method, amount) => {
        let orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        let session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        var counter = localStorage.getItem("pos_counter")
        counter = JSON.parse(counter)
        config_settings = counter['config_settings']
        let checkCustomer = orders[session_selected.sessionIndex].currentCustomer
        if (amount > 0 && $scope.amount_present > 0) {
            if (!checkCustomer && method.payment_type == "point" || checkCustomer && checkCustomer.length < 1 && method.payment_type == "point") {
                toastr.error("Bạn chưa nhập khách hàng!");

            } else if (checkCustomer && method.payment_type == "point" && checkCustomer.prp_reward_count < config_settings.reward_point_invoice_count) {
                toastr.error("Khách hàng không đủ điều kiện sử dụng điểm!");
            } else {
                if (!$scope.payments || $scope.payments && $scope.payments.length < 1) {
                    if (method.payment_type == "point" && amount > checkCustomer.pointToMoney && $scope.amount_present >= checkCustomer.pointToMoney) {
                        amount = checkCustomer.pointToMoney
                        toastr.error("Bạn đang nhập quá số lượng điểm khách hàng hiện có");
                    } else if (method.payment_type == "point" && amount >= $scope.amount_present && $scope.amount_present <= checkCustomer.pointToMoney) {
                        amount = $scope.amount_present
                    }
                    method.Amount = amount
                    $scope.payments.push(method)
                } else {
                    let loop = false
                    for (let i = 0; i < $scope.payments.length; i++) {
                        e = $scope.payments[i]
                        if (e.Id == method.Id) {
                            e.Amount += amount
                            loop = true
                            if (method.payment_type == "point" && e.Amount >= checkCustomer.pointToMoney && $scope.amount_present >= checkCustomer.pointToMoney) {
                                e.Amount -= amount
                                amount = checkCustomer.pointToMoney - e.Amount
                                e.Amount += amount
                                toastr.error("Bạn đang nhập quá số lượng điểm khách hàng hiện có");
                            } else if (method.payment_type == "point" && amount >= $scope.amount_present && $scope.amount_present <= checkCustomer.pointToMoney) {
                                e.Amount -= amount
                                amount = $scope.amount_present
                                e.Amount += amount
                            }
                        }
                    }
                    if (!loop) {
                        if (method.payment_type == "point" && amount >= checkCustomer.pointToMoney && $scope.amount_present >= checkCustomer.pointToMoney) {
                            amount = checkCustomer.pointToMoney
                            toastr.error("Bạn đang nhập quá số lượng điểm khách hàng hiện có");
                        } else if (method.payment_type == "point" && amount >= $scope.amount_present && $scope.amount_present <= checkCustomer.pointToMoney) {
                            amount = $scope.amount_present
                        }
                        method.Amount = amount
                        $scope.payments.push(method)
                    }
                }
                $scope.amount_present -= amount
                if ($scope.amount_present <= 0) {
                    $scope.amount_present = 0
                    $rootScope.isHidePaymentButton = true
                }
                $scope.currentAmount = $scope.amount_present
            }
            $rootScope.selectAllText('current-amount')
        }

        $rootScope.customerPay_present = 0
        for (i = 0; i < $scope.payments.length; i++) {
            $rootScope.customerPay_present += $scope.payments[i].Amount
        }

        if (amount > orders[session_selected.sessionIndex].customerPay) {
            $scope.hideSuggestAmount = true
        }
        // $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
        $scope.payingAmountSuggestion()
        $rootScope.selectAllText('current-amount')
        $rootScope.switchSuggest()
    }

    $rootScope.getDiscount = () => {
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        if (orders[session_selected.sessionIndex].typeDiscount == 0) {
            orders[session_selected.sessionIndex].discount = $scope.orderInfo.discountValues
            if ($rootScope.orderInfo.discountValues >= orders[session_selected.sessionIndex].totalAmount) {
                $rootScope.orderInfo.discountValues = orders[session_selected.sessionIndex].totalAmount
                orders[session_selected.sessionIndex].customerPay = 0
                orders[session_selected.sessionIndex].discountPercent = 100
            } else {
                orders[session_selected.sessionIndex].customerPay = orders[session_selected.sessionIndex].totalAmount - $scope.orderInfo.discountValues
                orders[session_selected.sessionIndex].discountPercent = parseFloat((orders[session_selected.sessionIndex].discount * 100 / orders[session_selected.sessionIndex].totalAmount).toFixed(2))
            }
            $rootScope.customerPay = orders[session_selected.sessionIndex].customerPay
        } else {
            if ($scope.orderInfo.discountValues >= 100) {
                orders[session_selected.sessionIndex].discountPercent = 100
                orders[session_selected.sessionIndex].discount = orders[session_selected.sessionIndex].totalAmount
                orders[session_selected.sessionIndex].customerPay = 0
            } else {
                orders[session_selected.sessionIndex].discountPercent = $rootScope.orderInfo.discountValues
                orders[session_selected.sessionIndex].customerPay = orders[session_selected.sessionIndex].totalAmount - ((orders[session_selected.sessionIndex].discountPercent * orders[session_selected.sessionIndex].totalAmount) / 100)
                orders[session_selected.sessionIndex].discount = ($rootScope.orderInfo.discountValues * orders[session_selected.sessionIndex].totalAmount) / 100
            }
            $rootScope.orderInfo.discountValues = orders[session_selected.sessionIndex].discountPercent
            $rootScope.customerPay = orders[session_selected.sessionIndex].customerPay
        }
        // $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
        localStorage.setItem('pos_orders', JSON.stringify(orders))
        $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
        $rootScope.PayingAmount()
    }


    $rootScope.PayingAmount = () => {
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
            // $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
        if (orders[session_selected.sessionIndex].CurrentPayments && orders[session_selected.sessionIndex].CurrentPayments.length > 0) {
            orders[session_selected.sessionIndex].CurrentPayments[0].Amount = $rootScope.orderInfo.payingamountValues
        } else {
            $scope.methodStrCurrent = 'Tiền mặt'
        }
        orders[session_selected.sessionIndex].payingAmount = $rootScope.orderInfo.payingamountValues
        orders[session_selected.sessionIndex].changeAmount = orders[session_selected.sessionIndex].payingAmount - orders[session_selected.sessionIndex].customerPay
        $rootScope.changeAmount = orders[session_selected.sessionIndex].changeAmount
        localStorage.setItem('pos_orders', JSON.stringify(orders))
    }

    $rootScope.switchSuggest = () => {
        $scope.isHideSuggest = false
            // console.log($scope.payments)
        if ($scope.payments.length == 0) {
            $scope.isHideSuggest = false
        } else if ($scope.payments.length > 0) {
            $scope.isHideSuggest = !$scope.isHideSuggest
        }
    }

    $scope.getSugges = (value) => {
        $rootScope.switchSuggest()
        if ($scope.payments.length > 0) {
            // $scope.isHideSuggest = false
            $scope.currentAmount = parseInt(value)

        } else {
            $scope.payment.cash.Amount = parseInt(value)
            $scope.payments.push($scope.payment.cash)
            $scope.save()
        }
    }

    $scope.save = () => {
        let orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        let session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        let pos_counter = localStorage.getItem('pos_counter')
        pos_counter = JSON.parse(pos_counter)
        config_settings = pos_counter["config_settings"]
        var total = 0
        for (let i = 0; i < $scope.payments.length; i++) {
            const e = $scope.payments[i]
            total += e.Amount
            if ($scope.payments[i].payment_type == "point") {
                $scope.payments[i]["point_used"] = Math.round($scope.payments[i].Amount / (config_settings.reward_point_money_to_point / config_settings.reward_point_point_to_money))
            }
        }
        orders[session_selected.sessionIndex].CurrentPayments = $scope.payments
        $rootScope.orderInfo.payingamountValues = total
        orders[session_selected.sessionIndex].payingAmount = $rootScope.orderInfo.payingamountValues
        orders[session_selected.sessionIndex].changeAmount = orders[session_selected.sessionIndex].payingAmount - orders[session_selected.sessionIndex].customerPay
        $rootScope.changeAmount = orders[session_selected.sessionIndex].changeAmount
        localStorage.setItem('pos_orders', JSON.stringify(orders))
        $scope.getCurrentPaymentMethodsToString()

    }
    $scope.methodStrCurrent = ''
    $scope.getCurrentPaymentMethodsToString = () => {
        let orders = localStorage.getItem('pos_orders')
        let session_selected = localStorage.getItem('pos_session_selected')
        if (session_selected && orders) {
            orders = JSON.parse(orders)
            session_selected = JSON.parse(session_selected)
            $scope.methodStrCurrent = ''
            angular.forEach(orders[session_selected.sessionIndex].CurrentPayments, (e) => {
                $scope.methodStrCurrent += `${e.MethodStr}, `
            })
        }

        return $scope.methodStrCurrent
    }
    $scope.getCurrentPaymentMethodsToString()
    $scope.isDisabled = () => {
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        if (session_selected && orders) {
            orders = JSON.parse(orders)
            session_selected = JSON.parse(session_selected)
            if (orders[session_selected.sessionIndex].CurrentPayments && orders[session_selected.sessionIndex].CurrentPayments.length > 1) {
                return true
            } else {
                return false
            }
        }
    }
    $scope.isDisableSave = () => {
        let orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        let session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        let checkBA = $scope.payments
        let flag = false
        angular.forEach(checkBA, (e) => {
            if (e.AccountId == null & e.bankAccounts != null) {
                flag = true
            } else {
                flag = false
            }
        });
        return flag
    }

    $scope.removePayment = (index) => {
        var orders = localStorage.getItem("pos_orders")
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem("pos_session_selected")
        session_selected = JSON.parse(session_selected)
        $scope.amount_present += $scope.payments[index].Amount
        $scope.currentAmount = $scope.amount_present
        $scope.payments.splice(index, 1)
        if ($scope.payments && $scope.payments < 1) {
            $scope.amount_present = orders[session_selected.sessionIndex].customerPay
            $scope.currentAmount = $scope.amount_present
        }
        if ($scope.amount_present > 0) {
            $rootScope.isHidePaymentButton = false
        }
        if (orders[session_selected.sessionIndex].changeAmount >= 0) {
            $scope.hideSuggestAmount = false
        }

        $('#current-amount').focus().select()
        let customer_payment = 0;
        for (let i = 0; i < $scope.payments.length; i++) {
            customer_payment += $scope.payments[i].Amount
        }
        // $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
        $rootScope.customerPay_present = customer_payment;
        $scope.payingAmountSuggestion()
        $rootScope.switchSuggest()
    }

    $scope.saveTransaction = () => {
            var orders = localStorage.getItem("pos_orders")
            orders = JSON.parse(orders)
            var session_selected = localStorage.getItem("pos_session_selected")
            session_selected = JSON.parse(session_selected)
            orders[session_selected.sessionIndex].description = $rootScope.orderInfo.Description ? $rootScope.orderInfo.Description : ''
            localStorage.setItem('pos_orders', JSON.stringify(orders))

            let pos_orders = orders[session_selected.sessionIndex]
            var counter = localStorage.getItem("pos_counter")
            counter = JSON.parse(counter)
            counter_config = counter['counter_config']
            $rootScope.loadedPayment = false;
            $http({
                method: "POST",
                url: "/api/payment",
                // headers: {
                //   'Content-type': 'application/json'
                // },
                // params:JSON.stringify(pos_orders),
                data: JSON.stringify({
                    "jsonrpc": "2.0",
                    "params": {
                        pos_orders,
                        counter_config
                    },
                }),
                dataType: "json",
            }).then(
                function mySuccess(response) {
                    $rootScope.loadedPayment = true;
                    if (typeof(response.data.error) !== "undefined") {
                        if (response.data.error.code == 200) {
                            return toastr.error(response.data.error.data['message']);
                        }
                    }
                    response = JSON.parse(response.data.result)
                    if (response['status'] == false || response['code'] == 400) {
                        return toastr.error(response['message']);
                    }
                    if (response['status'] == true || response['code'] == 200) {
                        $rootScope.closeTab(orders[session_selected.sessionIndex].id)
                        $rootScope.getProductList()
                        $rootScope.loadedPayment = true;
                        $rootScope.responseOrder = response.result[0]
                        $rootScope.getProductList()
                        $scope.searchCustomer = ""
                        var contents = buildContent($rootScope.responseOrder, $rootScope.invoiceType);
                        onPrint(contents)
                        response['message_tracebility'].length > 0 ? toastr.success(response['message_tracebility']) : null
                        return toastr.success(response['message']);
                    }
                },
                function myError() {
                    $rootScope.loadedPayment = true;
                })
        }
        // <html>
        //      <header>
        //       <meta name="viewport" content="width=device-width, initial-scale=1.0">
        //      </header>

    //   <body style="font-size: 0.75rem; font-family: Arial, Helvetica, sans-serif; margin:5px 10px 5px 5px"></body>
    buildContent = function(data, invoiceType) {
        var result
        if (invoiceType) {
            result = `
  <div class="billPrint" style="width:100%;">
        <center>
        <h6>${data.company_name}</h6>
        <p>${data.company_address}</p>
        <h4>HÓA ĐƠN BÁN HÀNG</h4>
          ${new Date().getDate()}/${(new Date().getMonth() + 1)}/${new Date().getFullYear()} <br>
          Số HĐ: ${data.order_name} <br>
        </center>
    <div id="top" style="font-size:10px;width: 100%;">
      <p>
        Quầy bán: ${data.counter_name}<br>
        NV: ${data.seller_name}<br>
      </p>

    </div> 

    <div id="mid" style="font-size:10px;width: 100%;"> 
      <p> 
        Khách hàng: ${data.partner_name} <br>
        SĐT: ${data.mobile}               <br>
        Địa chỉ: ${data.address}          <br>
      </p>
    </div>

    <div class="header-print" style=" float: left; width: 100%; border-top: 1px solid #000; border-bottom: 1px solid #000;">
      <div style="width: 40%; float: left;">
          <h4>Đơn Giá</h4>
      </div>
      <div style="width: 20%;float: left; text-align: center;">
          <h4>SL</h4>
      </div>
      <div style="width: 40%;float: left; text-align: right; margin-left:-3px">
          <h4>Thành Tiền</h4>
      </div>
    </div>  `

            data.lines.forEach((item, index) => {
                result += `
              <div class="body-print" style="width: 100%; border-bottom: dashed 1px #000; float: left;margin-top: 5px; padding-bottom:5px;">
                <div style="width:100% ; float: left;">${item.product_name} 	&nbsp;	&nbsp;	&nbsp; ${item.barcode}  </div>
                <div style="width: 40%;float: left">${item.change_price.toLocaleString()}</div>
                <div style="width: 20%;float: left; text-align: center;margin-left:-3px">${item.qty}</div>
                <div style="width: 40%;float: left; text-align: right; margin-left:-3px">${item.sub_total.toLocaleString()}</div>
              </div>`

            })

            result += `  
      <div  style="float:left; width:100%; text-align:left;margin-left:-5px; margin-top:10px; margin-bottom:10px; padding-top: 10px;font-size:11px;"> 
        <b>Tổng tiền hàng <pan style="width:50%">:</pan></b>  ${data.amount_total.toLocaleString()}<br> 
        <b>Chiết khẩu <span style="width:50%">:</span> </b>  ${data.discount.toLocaleString()}<br> 
        <b>Khách Trả<span style="width:50%">:</span> </b> ${data.amount_paid.toLocaleString()}<br> 
        <b>Trả Khách<span style="width:50%">:</span></b> ${data.amount_return.toLocaleString()}<br> 
      </div >
      <p style="text-align:center;"> <i>Cảm ơn và hẹn gặp lại</i></p>
   
    </div>`
        } else {
            result = `
<div class="modal-body" id="print-order">
<h5 class="text-center">HÓA ĐƠN BÁN HÀNG</h5>
    <h6 class="text-center mb-4 ng-binding">
        Số hóa đơn:${data.order_name}
    </h6>
    <h6 class="text-center mb-4 ng-binding">
       ${'Ngày ' + new Date().getDate() + ' tháng ' + (new Date().getMonth() + 1) + ' năm ' + new Date().getFullYear()}
    </h6>

    <h6 class="text-left mb-4 ng-binding">
        Khách hàng:${data.partner_name} <br>
        Người bán :${data.seller_name} <br>
        Tổng tiền hàng: ${data.amount_total.toLocaleString()} VNĐ <br> 
        Chiết khẩu: ${data.discount.toLocaleString()} VNĐ <br>
        Khách phải trả: ${data.customer_pay.toLocaleString()} VNĐ<br> 
        Khách đưa: ${data.amount_paid.toLocaleString()} VNĐ<br> 
        Trả khách: ${data.amount_return.toLocaleString()} VNĐ<br> 
    </h6>
    <table class="table table-striped">
<thead>
  <tr>
  <th scope="col">#</th>
  <th scope="col">Tên</th>
  <th scope="col">Đơn giá</th>
  <th scope="col">Số lượng</th>
  <th scope="col">Chiết khẩu</th>
  <th scope="col">Thành tiền</th>
  </tr>
</thead>
    <tbody>`;
            data.lines.forEach((item, index) => {
                result += `
        <tr ng-repeat="item in responseOrder.lines">
          <th scope="row">${index+1}</th>
          <td>${item.product_name}</td>
          <td>${item.price_unit.toLocaleString() }</td>
          <td>${item.qty}</td>
          <td>${item.discount.toLocaleString() }</td>
          <td>${item.sub_total.toLocaleString()}</td>
        </tr>
        `;

            });
            result += `
    </tbody>
    </table>
      </div>`
        }
        console.log('result', result)
        return result;
    }

    onPrint = (contents) => {
        var body = document.getElementsByTagName("BODY")[0];
        var frame1 = document.createElement("IFRAME");
        frame1.name = "frame1";
        frame1.setAttribute("style", "position:absolute;top:-1000000px");
        body.appendChild(frame1);
        var frameDoc = frame1.contentWindow ? frame1.contentWindow : frame1.contentDocument.document ? frame1.contentDocument.document : frame1.contentDocument;
        frameDoc.document.open();
        frameDoc.document.write(
            '<html> <head> <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"></head><body style="font-size: 0.75rem; font-family: Arial, Helvetica, sans-serif; margin:5px 10px 5px 5px">' + contents + '</body></html>');
        frameDoc.document.close();
        window.setTimeout(function() {
            window.frames["frame1"].focus();
            window.frames["frame1"].print();
            body.removeChild(frame1);
        }, 500);
    }

    setTimeout($scope.getPaymentMethod, 800)

}]);