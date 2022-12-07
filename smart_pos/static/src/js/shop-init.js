// Create an Application named "myApp".
var app = angular.module("myApp", ['ngSanitize']);
app.directive('compile', ['$compile', function($compile) {
    return function(scope, element, attrs) {
        scope.$watch(
            function(scope) {
                return scope.$eval(attrs.compile);
            },
            function(value) {
                element.html(value);
                $compile(element.contents())(scope);
            }
        )
    };
}])

app.service("configService", function($http) {
    let pos_context = JSON.parse(JSON.parse(sessionStorage.getItem('current_action')))
    var swift_code = new URLSearchParams(document.location.search).get("swift_code")
    this.loadConfigFromAPI = () => $http.post('/api/load-session-config', {
        "id": 345345345,
        "jsonrpc": "2.0",
        "params": { 'swift_code': swift_code, 'uid': pos_context.context.uid }

    })
    this.saveConfig = (cfg) => {
        this.sessionConfig = cfg
        if (cfg) {

            localStorage.setItem('pos_counter', JSON.stringify(cfg))
        }

    }

    this.getConfig = () => {
        let _config = localStorage.getItem('pos_counter');
        if (_config) {
            return JSON.parse(_config)
        } else {
            return null
        }
    }
})
app.controller("myCtrl", ['$scope', '$rootScope', '$timeout', '$http', 'configService', function($scope, $rootScope, $timeout, $http, configService) {

    configService.loadConfigFromAPI().then((res) => {
        configService.saveConfig(res.data.result)

        let pos_counter = configService.getConfig()
            // let pos_counter = localStorage.getItem('pos_counter')
            // pos_counter = JSON.parse(pos_counter)
        $rootScope.loaded = false;
        $rootScope.loadedPayment = false;
        $scope.operator = "+";
        $rootScope.tabCode = 0;
        $scope.variable1 = 30;
        $scope.variable2 = 20;
        $scope.result = 0;
        $rootScope.invoiceType = true
        $scope.typed_into = false
        $scope.barcode_scanner_active = pos_counter.counter_config.barcode_scanner
        $rootScope.selectAllText = (id) => {
            const text_select = document.getElementById(id);
            text_select.focus(); // text_select.setSelectionRange(0, text_select.length);
        }


    }, (err) => {

    })


    $timeout(function() {
        $rootScope.loaded = true;
        $rootScope.loadedPayment = true;
    }, 2000);
    $('#productSearchInput').on({
        keypress: function(e) { if (e.which == 13) { $scope.typed_into = true } },
        change: function() {
            let barcode_scan = $(this).val()
            if ($scope.typed_into) {
                $scope.searchParam = ""
                let flag_scan = false
                angular.forEach($rootScope.productList, (e) => {
                    if (e.barcode === barcode_scan) {
                        $rootScope.selectProduct(e)
                        flag_scan = true
                        $rootScope.productAutoHide = false
                        toastr.info(`Mặt hàng ${e.name} được thêm vào`);
                    }
                })
                if (!flag_scan) {
                    toastr.error("Không tìm thấy sản phẩm có mã ", barcode_scan);
                }

                $rootScope.productAutoHide = false
                $timeout(function() {
                    $("#productSearchInput").focus().select()
                }, 10);
                $scope.typed_into = false; //reset type listener
            }
        }
    });

    // $('#productSearchQrInput').on({
    //   keypress: function() { $scope.typed_into = true; },
    //   change: function() {
    //       if ($scope.typed_into) {
    //           alert('type');
    //           $scope.typed_into = false; //reset type listener
    //       }
    //   }
    // });
    $scope.setOperatorSum = function() {
        $scope.operator = "+";
    }

    $scope.setOperatorMinus = function() {
        $scope.operator = "-";
    }

    $scope.calculate = function() {
        if ($scope.operator == "+") {
            $scope.result = parseFloat($scope.variable1) + parseFloat($scope.variable2);
        } else if ($scope.operator == "-") {
            $scope.result = parseFloat($scope.variable1) - parseFloat($scope.variable2);
        }
    }

    var a = 1
    $scope.createNewTab = () => {
        $scope.tabCode = a++;
    }

    $scope.deleteProd = (index) => {
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        var e = orders[session_selected.sessionIndex]

        angular.forEach(e.tracebility_code, (value, key) => {
            if (value == e.items[index].id) {
                delete e.tracebility_code[key]
            }
        })

        e.totalAmount -= e.items[index].total
        e.totalQuantity -= e.items[index].quantity
        e.items.splice(index, 1)

        $rootScope.total_Bill = e.totalAmount
        $rootScope.total_Quantity = e.totalQuantity
        e.customerPay = e.totalAmount - e.discount
        $rootScope.customerPay = e.customerPay
        if (e.items.length <= 0) {
            e.customerPay = 0
            e.payingAmount = 0
            e.changeAmount = 0
            $rootScope.customerPay = e.customerPay
            $rootScope.changeAmount = e.changeAmount
            $rootScope.orderInfo.payingamountValues = e.payingAmount
        } else {
            $rootScope.customerPay = e.customerPay
        }
        $rootScope.orderInfo.payingamountValues = e.customerPay
        localStorage.setItem('pos_orders', JSON.stringify(orders))
        $rootScope.getDiscount()
        $rootScope.PayingAmount()
    }

    $scope.hideQuantity = true
    $scope.isHideMode = true
    $scope.isQrMode = false
    $scope.changeSaleMode = () => {
        if (!$scope.hideQuantity || !$scope.isHideMode) {
            toastr.info("Chế độ nhập nhanh");
            return [$scope.hideQuantity = true, $scope.isHideMode = true]
        }
        toastr.info("Chế độ nhập thường");
        return [$scope.hideQuantity = false, $scope.isHideMode = false, $scope.isQrMode = false]
    }

    $scope.changeQrMode = () => {
        if (!$scope.isQrMode) {
            toastr.info("Chế độ nhập QR")
            $timeout(function() {
                $("#productSearchQrInput").focus().select()
            }, 100);
            return [$scope.hideQuantity = true, $scope.isHideMode = true, $scope.isQrMode = true]
        }
        toastr.info("Chế độ nhập nhanh");
        $timeout(function() {
            $("#productSearchInput").focus().select()
        }, 100)
        return $scope.isQrMode = false
    }
    $rootScope.productAutoHide = false
    $(document).mouseup(function(e) {
        var container = $(".autocomplete-prod");
        if (!container.is(e.target) && container.has(e.target).length === 0) {
            $rootScope.productAutoHide = false
        }
    });

    $scope.onSearching = (s) => {
        if (s && s.length > 0) {
            return $rootScope.productAutoHide = true
        } else {
            return $rootScope.productAutoHide = false
        }
    }

    $scope.onSearchingQr = (s) => {
        let code_id = s.split("/")
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        var orderNow = orders[session_selected.sessionIndex]
        $http({
            method: "POST",
            url: "/api/get-product-tracebility-by-code",
            params: { 'code': code_id[3] }
        }).then(function mySuccess(res) {
            if (res.data.status == true) {
                let flag = false
                angular.forEach($rootScope.productList, (e) => {
                    if (res.data.data.product_id == e.traceability_id) {
                        orderNow.tracebility_code[code_id[3]] = e.id
                        localStorage.setItem('pos_orders', JSON.stringify(orders))
                        $rootScope.selectProduct(e)
                        flag = true
                    }
                })
                if (flag == false) {
                    toastr.error("Không có sản phẩm nào có mã QR tương ứng")
                }
            } else {
                toastr.error(res.data.message)
            }
        }, function myError(res) {
            toastr.error(res.data.message)
        })
        $scope.searchParamQR = ""
        $timeout(function() {
            $("#productSearchQrInput").focus().select()
        }, 100);

    }

    $scope.selectedProduct = {}

    $scope.itemClicked = (prod) => {
        $rootScope.productAutoHide = false

        if ($scope.hideQuantity) {
            $rootScope.selectProduct(prod)
        } else {
            $scope.searchParam = prod.defaultCode + ' ' + prod.name
            $scope.selectedProduct = prod
            $timeout(function() {
                $('#productQtyInput').focus().select()
            }, 100);
        }

    }
    $scope.onChangeQuantity = () => {
        if ($scope.selectedProduct && $scope.selectedProduct.length > 0) {
            $scope.selectedProduct.quantity = $scope.productQty
            $rootScope.selectProduct($scope.selectedProduct)
            delete $scope.selectedProduct.quantity
            $scope.selectedProduct = {}
            $scope.searchParam = null
            $scope.productQty = null
        } else {
            toastr.error("Bạn chưa nhập sản phẩm");
        }

    }
    $scope.price_item = {}

    $scope.typeDiscount = true

    $scope.changePrintPaper = () => {
        $rootScope.invoiceType = !$rootScope.invoiceType
        if ($rootScope.invoiceType) {
            toastr.info("Chế độ in khổ nhỏ");
        } else if (!$rootScope.invoiceType) {
            toastr.info("Chế độ in khổ to");
        }
    }


}]);

app.directive('smlEnter', function() {
    return function(scope, element, attrs) {
        element.bind("keydown keypress", function(event) {
            if (event.which === 13) {
                scope.$apply(function() {
                    scope.$eval(attrs.smlEnter);
                });

                event.preventDefault();
            }
        });
    };
});

app.controller("disCtrl", ['$scope', '$rootScope', function($scope, $rootScope) {

    $rootScope.setInfoProd = (index) => {
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        orders = JSON.parse(orders)
        session_selected = JSON.parse(session_selected)
        const orderNow = orders[session_selected.sessionIndex].items[index]
        $scope.price_item.onHand = orderNow.onHand
        $scope.price_item.onHold = orderNow.onHold
    }


    $rootScope.setPrice = (index) => {
        // removeAttrSetPrice()
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        orders = JSON.parse(orders)
        session_selected = JSON.parse(session_selected)
        const orderNow = orders[session_selected.sessionIndex].items[index]
        $scope.price_item.unitPrice = orderNow.basePrice
        $scope.price_item.salePrice = orderNow.salePrice
        $scope.price_item.onHand = orderNow.onHand
        $scope.price_item.onHold = orderNow.onHold
        $scope.price_item.cost = orderNow.cost
            // $scope.price_item.cost = orderNow.originPrice
            // console.log(orderNow.cost)

        if (orderNow.typeDiscount == 0) {
            $scope.price_item.discountProdValues = orderNow.discountProd
            orderNow.discountRatio = null
            $scope.price_item.selected = true
        } else if (orderNow.typeDiscount == 1) {
            $scope.price_item.discountProdValues = orderNow.discountProdPercent
            $scope.price_item.selected = false
            orderNow.discountRatio = orderNow.discountProdPercent
        } else {
            $scope.price_item.discountProdValues = 0
            $scope.price_item.selected = true
        }
        $scope.discounted = $scope.price_item.unitPrice
        return $scope.price_item.selected
    }

    $scope.select = (value, index) => {
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        orders = JSON.parse(orders)
        session_selected = JSON.parse(session_selected)
        const orderNow = orders[session_selected.sessionIndex].items[index]
        if (value == 'vnd') {
            orderNow.discountRatio = null
            $rootScope.currentCart.items[index].discountRatio = orderNow.discountRatio
            $rootScope.currentCart.items[index].discountProdVND = orderNow.discountProdVND
            orderNow.typeDiscount = 0
            $scope.price_item.discountProdValues = orderNow.discountProdVND
            localStorage.setItem('pos_orders', JSON.stringify(orders))
            return $scope.price_item.selected = true
        } else {
            orderNow.discountProdPercent = (orderNow.discountProd == 0) ? 0 : orderNow.discountProdPercent
            orderNow.discountRatio = orderNow.discountProdPercent
            $rootScope.currentCart.items[index].discountRatio = orderNow.discountRatio
            orderNow.typeDiscount = 1
                // $scope.price_item.discountProdValues = parseFloat((orderNow.discountProdPercent).toFixed(2))
            $scope.price_item.discountProdValues = Math.round((orderNow.discountProdPercent + Number.EPSILON) * 100) / 100

            localStorage.setItem('pos_orders', JSON.stringify(orders))
            return $scope.price_item.selected = false
        }
        // $scope.$apply()
    }
    $scope.changeBasePrice = (index) => {
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        orders = JSON.parse(orders)
        session_selected = JSON.parse(session_selected)
    }
    $scope.newChangePrice = (index) => {
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        orders = JSON.parse(orders)
        session_selected = JSON.parse(session_selected)
        const orderNow = orders[session_selected.sessionIndex].items[index]
        $scope.price_item.unitPrice = (!$scope.price_item.unitPrice) ? 0 : $scope.price_item.unitPrice
        orderNow.basePrice = $scope.price_item.unitPrice
        orderNow.salePrice = orderNow.basePrice
            // $rootScope.currentCart.items[index].salePrice = orderNow.basePrice  
        $rootScope.currentCart.items[index] = orderNow
        $scope.price_item.salePrice = orderNow.basePrice
        localStorage.setItem('pos_orders', JSON.stringify(orders))
        $rootScope.changeTotal($rootScope.currentCart.items[index])
    }
    $scope.discOnProd = (index) => {
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        orders = JSON.parse(orders)
        session_selected = JSON.parse(session_selected)
        const orderNow = orders[session_selected.sessionIndex].items[index]
        if ($scope.price_item.selected == true) {
            if ($scope.price_item.discountProdValues >= $scope.price_item.unitPrice) {
                $scope.price_item.discountProdValues = $scope.price_item.unitPrice
                orderNow.discountProdPercent = 100
                    // orderNow.discountProdVND = $scope.price_item.discountProdValues
                    // orderNow.discountProd = $scope.price_item.discountProdValues
                orderNow.salePrice = 0
            } else {
                // orderNow.discountProdVND = $scope.price_item.discountProdValues
                // orderNow.discountProd = $scope.price_item.discountProdValues
                orderNow.salePrice = $scope.price_item.unitPrice - $scope.price_item.discountProdValues
                orderNow.discountProdPercent = parseFloat((100 - (orderNow.salePrice * 100) / $scope.price_item.unitPrice).toFixed(2))
            }
            orderNow.discountProdVND = $scope.price_item.discountProdValues
            orderNow.discountProd = $scope.price_item.discountProdValues

        } else {
            if ($scope.price_item.discountProdValues >= 100) {
                $scope.price_item.discountProdValues = 100
                orderNow.discountProdPercent = 100
                orderNow.discountProdVND = $scope.price_item.unitPrice
                orderNow.discountProd = orderNow.discountProdVND
                orderNow.salePrice = 0

            } else {
                orderNow.discountProdPercent = $scope.price_item.discountProdValues
                orderNow.salePrice = $scope.price_item.unitPrice - ($scope.price_item.unitPrice * $scope.price_item.discountProdValues) / 100
                orderNow.discountProdVND = ($scope.price_item.unitPrice * $scope.price_item.discountProdValues) / 100
                orderNow.discountProd = orderNow.discountProdVND
            }
            orderNow.discountRatio = orderNow.discountProdPercent
        }
        // $rootScope.currentCart.items[index].salePrice = orderNow.salePrice
        $rootScope.currentCart.items[index] = orderNow
        $scope.price_item.salePrice = orderNow.salePrice
        localStorage.setItem('pos_orders', JSON.stringify(orders))
        $rootScope.changeTotal($rootScope.currentCart.items[index])
    }
    $scope.ajustedPrice = (index) => {
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        orders = JSON.parse(orders)
        session_selected = JSON.parse(session_selected)
        const orderNow = orders[session_selected.sessionIndex].items[index]
        $scope.price_item.salePrice = (!$scope.price_item.salePrice) ? 0 : $scope.price_item.salePrice
        if ($scope.price_item.selected == true) {
            if ($scope.price_item.salePrice <= $scope.price_item.unitPrice) {
                $scope.price_item.discountProdValues = $scope.price_item.unitPrice - $scope.price_item.salePrice
            } else {
                $scope.price_item.discountProdValues = 0
            }
            orderNow.discountProd = $scope.price_item.discountProdValues
            orderNow.discountProdVND = $scope.price_item.discountProdValues
            orderNow.discountProdPercent = (orderNow.discountProdVND / $scope.price_item.unitPrice) * 100
        } else {
            if ($scope.price_item.salePrice <= $scope.price_item.unitPrice) {
                $scope.price_item.discountProdValues = 100 - ($scope.price_item.salePrice * 100) / $scope.price_item.unitPrice
            } else {
                $scope.price_item.discountProdValues = 0
            }

            orderNow.discountProdPercent = $scope.price_item.discountProdValues
            orderNow.discountProdVND = (orderNow.discountProdPercent * $scope.price_item.unitPrice) / 100
        }
        $scope.saleLtCost = false
        if ($scope.price_item.salePrice < $scope.price_item.cost) {
            $scope.saleLtCost = true
        }
        orderNow.salePrice = $scope.price_item.salePrice
        localStorage.setItem('pos_orders', JSON.stringify(orders))
            // $rootScope.currentCart.items[index].salePrice = orderNow.salePrice
        $rootScope.currentCart.items[index] = orderNow
        $rootScope.changeTotal($rootScope.currentCart.items[index])
            // console.log(orderNow.salePrice)
    }

    $scope.shouldBeOpen = true;
}])

app.directive('popoverDirective', ['$compile', function($compile) {
    return {
        restrict: 'EAC',
        link: function(scope, elements, attrs) {
            $('[data-toggle="popover"]').popover({
                // 'placement': 'left',
                'trigger': 'click',
                'html': true,
                'container': 'body',
                'content': function() {
                    var content = $(this).attr("data-popover-content")
                    return $compile($(content).children(".discount-form").html())(scope);
                }
            });
            // if (attrs.toggle=="tooltip"){
            //   $(element).tooltip();
            // }
            // if (attrs.toggle=="popover"){
            //   $(element).popover();
            // }
        }
    }
}]);

// app.directive('toggle', function(){
//   return {
//     restrict: 'A',
//     link: function(scope, element, attrs){
//       if (attrs.toggle=="tooltip"){
//         $(element).tooltip();
//       }
//       if (attrs.toggle=="popover"){
//         $(element).popover();
//       }
//     }
//   };
// });
app.directive('restrictInput', function() {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attr, ctrl) {
            ctrl.$parsers.unshift(function(viewValue) {
                var options = scope.$eval(attr.restrictInput);
                if (!options.regex && options.type) {
                    switch (options.type) {
                        case 'digitsOnly':
                            options.regex = '^[0-9]*$';
                            break;
                        case 'lettersOnly':
                            options.regex = '^[a-zA-Z]*$';
                            break;
                        case 'lowercaseLettersOnly':
                            options.regex = '^[a-z]*$';
                            break;
                        case 'uppercaseLettersOnly':
                            options.regex = '^[A-Z]*$';
                            break;
                        case 'lettersAndDigitsOnly':
                            options.regex = '^[a-zA-Z0-9]*$';
                            break;
                        case 'validPhoneCharsOnly':
                            options.regex = '^[0-9 ()/-]*$';
                            break;
                        default:
                            options.regex = '';
                    }
                }
                var reg = new RegExp(options.regex);
                if (reg.test(viewValue)) { //if valid view value, return it
                    return viewValue;
                } else { //if not valid view value, use the model value (or empty string if that's also invalid)
                    var overrideValue = (reg.test(ctrl.$modelValue) ? ctrl.$modelValue : '');
                    element.val(overrideValue);
                    return overrideValue;
                }
            });
        }
    }
});



$(function() {

    // $('.tab-item').on('click', function(){
    //     $('.tab-item').removeClass('selected');
    //     $(this).addClass('selected');
    // });


    // console.log('Chieu tao tong ',$("#page-left").height())
    // $("#product-items").resizable();
    // $('#product-items').resize(function(){
    // $('#order-items').height($("#page-left").height()-$("#product-items").height()); 
    // console.log('Chieu tao tong ',$("#page-left").height())
    // });
    // $(window).resize(function(){
    // $('#order-items').height($("#page-left").height()-$("#product-items").height()); 
    // //  $('#div1').height($("#parent").height()); 
    // });

    // const init = ()=>{



    //     $('#tab-1').attr('id',firstOrderTabId)


    // }

    //  

    // $('#new-tab').click(()=>{
    //     var orders = localStorage.getItem('pos_orders')
    //     orders = JSON.parse(orders)

    //     lastOrder = orders[orders.length-1] 
    //     orderId = Date.now()
    //     orderName = `Hóa đơn ${lastOrder.idx+1}`
    //     orderIdx = lastOrder.idx+1
    //     $('.tabbar .tab-move-right').before(`<li class="tab-item" id="${orderId}" >
    //     <a href="#">  ${orderName} </a>
    //  </li>`)
    //             order = {
    //                 id: orderId,
    //                 name: orderName,
    //                 idx: orderIdx,
    //                 items:[],
    //                 seller: {

    //                 },
    //                 buyer:{ 
    //                 },
    //                 totalAmount: 0, 
    //             }
    //     console.log(orders.length)
    //     orders.push(order)
    //     localStorage.setItem('pos_orders', JSON.stringify(orders))
    // })
})