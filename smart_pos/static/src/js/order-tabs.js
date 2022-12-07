app.controller("tabCtr", ['$scope', '$rootScope', '$timeout', function($scope, $rootScope, $timeout) {

    $rootScope.get_product = () => {
        var orders = localStorage.getItem("pos_orders")
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem("pos_session_selected")
        session_selected = JSON.parse(session_selected)
        for (let i = 0; i < orders.length; i++) {
            const e = orders[i];
            if ($rootScope.selected == e.id) {
                $rootScope.currentCart = {
                    items: e.items
                }
                $rootScope.total_Bill = e.totalAmount;
                $rootScope.total_Quantity = e.totalQuantity;
                $rootScope.discountValues = e.discount
                $rootScope.customerPay = e.customerPay;
                $rootScope.currentCustomer = e.currentCustomer
                $rootScope.payingamountValues = e.payingAmount
                $rootScope.changeAmount = e.changeAmount
                $rootScope.typeDiscount = e.typeDiscount
            }
        }
        // $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
    }
    $rootScope.selectDiscountType = (value) => {
        var orders = localStorage.getItem('pos_orders')
        var session_selected = localStorage.getItem('pos_session_selected')
        orders = JSON.parse(orders)
        session_selected = JSON.parse(session_selected)
        $timeout(function() {
            $('#discount-all').focus().select()
        }, 100)

        if (value == 'vnd') {
            orders[session_selected.sessionIndex].typeDiscount = 0
            $rootScope.orderInfo.discountValues = orders[session_selected.sessionIndex].discount
            localStorage.setItem('pos_orders', JSON.stringify(orders))
            return $rootScope.discount_type.selected = true
        }
        if (value == 'percent') {
            orders[session_selected.sessionIndex].typeDiscount = 1
            $rootScope.orderInfo.discountValues = orders[session_selected.sessionIndex].discountPercent
            localStorage.setItem('pos_orders', JSON.stringify(orders))
            return $rootScope.discount_type.selected = false
        }
    }
    $scope.selectOrder = (id, index) => {
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        session_selected = {
            sessionId: 0,
            sessionIndex: 0,
        }
        session_selected.sessionId = id
        session_selected.sessionIndex = index
        localStorage.setItem('pos_session_selected', JSON.stringify(session_selected))
        $rootScope.selected = session_selected.sessionId
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        let get_discount = 0
        orders.forEach((item) => {
            if (item.id == id) {
                $rootScope.orderInfo = {
                    Description: $rootScope.description,
                    discountValues: get_discount,
                    payingamountValues: item.payingAmount
                }
                return $rootScope.tabCode = item.idx
            }
        })
        $rootScope.discount_type = {}
        if (orders[session_selected.sessionIndex].typeDiscount == 0) {
            // $rootScope.discount_type = {selected : true}
            $rootScope.selectDiscountType('vnd')
                // get_discount = orders[session_selected.sessionIndex].discount
        } else {
            // $rootScope.discount_type = {selected : false}
            $rootScope.selectDiscountType('percent')
                // get_discount = orders[session_selected.sessionIndex].discountPercent
        }

        $rootScope.currentIndex = index
        $rootScope.get_product()
    }

    const initFunc = () => {
        // let currenctAction = JSON.parse(JSON.parse(sessionStorage.getItem('current_action')))
        // $rootScope.managerUrl = `/web#action=${currenctAction.id}&model=pos.counter&view_type=kanban`
        $scope.tabArrowDisable = true
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        let pos_counter = localStorage.getItem('pos_counter')
        pos_counter = JSON.parse(pos_counter)
        $rootScope.seller = pos_counter["seller"]
        if (!orders || orders && orders.length < 1) {
            const orderId = Date.now()
            session_selected = {
                sessionId: 0,
                sessionIndex: 0,
            }
            session_selected.sessionId = orderId
            session_selected.sessionIndex = 0
            $rootScope.selected = orderId


            var orders = [{
                id: orderId,
                name: 'Hóa đơn 1',
                idx: 1,
                items: [],
                // items: prod,
                seller: $rootScope.seller,
                // buyer: {

                // },
                CurrentPayments: [],
                changeAmount: 0,
                /* tiá»n thá»«a tráº£ láº¡i */
                payingAmount: 0,
                /* khÃ¡ch thanh toÃ¡n */
                customerPay: 0,
                /* khÃ¡ch cáº§n tráº£ */
                discount: 0,
                discountPercent: 0,
                typeDiscount: 0,
                totalQuantity: 0,
                totalAmount: 0,
                /* Tá»•ng tiá»n hÃ ng */
                description: '',
                tracebility_code: {},

            }]

            localStorage.setItem('pos_orders', JSON.stringify(orders))
            localStorage.setItem('pos_session_selected', JSON.stringify(session_selected))
                // console.log('orders',orders)
            $scope.selectOrder($rootScope.selected, 0)
            $rootScope.get_product()
            return $scope.orderTabs = orders
        }
        $rootScope.selected = session_selected.sessionId
        $scope.selectOrder(session_selected.sessionId, session_selected.sessionIndex)
        $rootScope.get_product()
        return $scope.orderTabs = orders

    }





    // $scope.tabName = `HÃ³a Ä‘Æ¡n 1`;
    // $scope.tabIndex = 0;
    // $scope.tabNo = 1; 
    // $scope.menuTab =` <li class="tab-item" id="${orderId}" >
    //                     <a href="#" ng-click="selectOrder(${orderId})" > Hoa don 1 </a>
    //                 </li>
    //                 <li class="tab-move-right">
    //                 <a href="#"> > </a>
    //                 </li> 
    //                 <li class="add-tab" id="new-tab">
    //                 <a href="#" ng-click="createTab()"> + </a>
    //                 </li>`
    // $scope.orderTab = ` <li class="tab-item" id="${orderId}" >
    //                     <a href="#" ng-click="selectOrder(${orderId})" > Hoa don 1 </a>
    //                 </li>`



    $scope.createTab = () => {
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)

        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)

        var navwidth = $(".tabbar");

        let lastOrder, orderId, orderName, orderIdx
        if (orders && orders.length < 1) {
            lastOrder = 0
            orderId = Date.now()
            orderName = `Hóa đơn 1`
            orderIdx = 1


        } else {
            lastOrder = orders[orders.length - 1]
            orderId = Date.now()
            orderName = `Hóa đơn ${lastOrder.idx+1}`
            orderIdx = lastOrder.idx + 1

        }


        $scope.orderTabs.push({
            id: orderId,
            idx: orderIdx,
            name: orderName
        })

        $rootScope.tabCode = orderIdx
        $scope.orderTab = `${$scope.orderTab}<li class="tab-item" id="${orderId}">
        <a href="#" ng-click="selectOrder(${orderId})">${orderName}</a>
     </li>`
        $scope.menuTab = `${$scope.orderTab} <li class="tab-move-right">
                    <a href="#"> > </a>
                    </li> 
                    <li class="add-tab" id="new-tab">
                    <a href="#" ng-click="createTab()"> + </a>
                    </li>`
        order = {
            id: orderId,
            name: orderName,
            idx: orderIdx,
            items: [],
            seller: $rootScope.seller,
            CurrentPayments: [],
            changeAmount: 0,
            payingAmount: 0,
            discount: 0,
            discountPercent: 0,
            typeDiscount: 0,
            // buyer: {},
            customerPay: 0,
            totalQuantity: 0,
            totalAmount: 0,
            description: '',
            tracebility_code: {},
        }

        orders.push(order)
        session_selected.sessionId = orderId
        session_selected.sessionIndex = orderIdx - 1
        localStorage.setItem('pos_orders', JSON.stringify(orders))
        localStorage.setItem('pos_session_selected', JSON.stringify(session_selected))
        $scope.selectOrder(session_selected.sessionId, session_selected.sessionIndex)
        if (navwidth.width() >= 450) {
            $scope.tabArrowDisable = false
            let _scrollTo = navwidth.scrollLeft() + 300
            navwidth.scrollLeft(_scrollTo);
        }


    }



    $rootScope.closeTab = (id) => {
        var orders = localStorage.getItem('pos_orders')
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem('pos_session_selected')
        session_selected = JSON.parse(session_selected)
        var navwidth = $(".tabbar").width();

        if (navwidth <= 449) {
            $scope.tabArrowDisable = true
        }
        $scope.orderTabs.forEach((item, idx) => {
            if (item.id == id) {
                return $scope.orderTabs.splice(idx, 1)
            }
        })
        orders.forEach((item, idx) => {
            if (item.id == id) {
                orders.splice(idx, 1)
                localStorage.setItem('pos_orders', JSON.stringify(orders))
            }
        })

        if (!orders || orders && orders.length < 1) {
            $scope.createTab()
                // $scope.selectOrder(orders[session_selected.sessionIndex ].id)
        } else if (orders[session_selected.sessionIndex] > 1 && session_selected.sessionId == id) {
            $scope.selectOrder(orders[session_selected.sessionIndex - 1].id, session_selected.sessionIndex - 1)
        } else {
            $scope.selectOrder(orders[0].id, 0)
        }

    }



    $rootScope.changeTotal = (prod) => {
        var total = 0;
        var quantity = 0;
        var orders = localStorage.getItem("pos_orders")
        orders = JSON.parse(orders)
        var session_selected = localStorage.getItem("pos_session_selected")
        session_selected = JSON.parse(session_selected)
        if (prod.quantity < 0) {
            quantity = 0
        } else {
            prod.total = prod.quantity * prod.salePrice
            orders.forEach((e) => {
                if ($rootScope.selected == e.id) {
                    e.items.forEach((ele) => {
                        if (ele.id == prod.id) {
                            ele.quantity = prod.quantity
                            ele.total = prod.total
                        }
                        total += ele.total
                        quantity += ele.quantity
                    })
                    e.customerPay = total
                    e.totalAmount = total
                    e.totalQuantity = quantity
                    $rootScope.total_Quantity = e.totalQuantity
                    $rootScope.total_Bill = e.totalAmount
                    $rootScope.customerPay = e.customerPay

                }
            })
        }
        localStorage.setItem('pos_orders', JSON.stringify(orders))
        $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
        $rootScope.PayingAmount()
        $rootScope.getDiscount()

    }

    $scope.moveToLeft = () => {
        var navwidth = $(".tabbar");
        navwidth.scrollLeft(navwidth.scrollLeft() - 300);
    }

    $scope.moveToRight = () => {
        var navwidth = $(".tabbar");
        let _scrollTo = navwidth.scrollLeft() + 300
        navwidth.scrollLeft(_scrollTo);
    }

    // $rootScope.deleteProd = (index) => {
    //     var orders = localStorage.getItem('pos_orders')
    //     orders = JSON.parse(orders)
    //     var e = orders[$rootScope.currentIndex].items
    //     e.splice(index, 1)
    //     localStorage.setItem('pos_orders', JSON.stringify(orders))
    // }

    setTimeout(initFunc, 800)

}])