app.controller("productCtrl", [
    "$scope",
    "$rootScope",
    "$http",
    "$compile",
    function($scope, $rootScope, $http, $compile) {
        $rootScope.productList = [];
        $rootScope.getProductList = () => {
            let pos_counter = localStorage.getItem('pos_counter')
            pos_counter = JSON.parse(pos_counter)
            $rootScope._picking_type = { '_picking_type': pos_counter["counter_config"]["_picking_type"] }
            $http({
                method: "GET",
                url: "/api/product",
                params: $rootScope._picking_type,
            }).then(function mySuccess(response) {
                $rootScope.productList = response.data
            }, function myError(response) {})
        }
        $scope.page = 0;
        $scope.itemsLimit = 6;


        Page = Math.ceil($rootScope.productList.length / $scope.itemsLimit);

        $scope.itemsPaginated = function() {
            const height = $("#product-items").height();
            const row = Math.ceil((height - 40) / 132);

            $scope.itemsLimit = 6 * row;
            // $scope.itemsLimit = 6
            $scope.totalPage = Math.ceil(
                $rootScope.productList.length / $scope.itemsLimit
            );
            var currentPageIndex = $scope.page * $scope.itemsLimit;
            return $rootScope.productList.slice(
                currentPageIndex,
                currentPageIndex + $scope.itemsLimit
            );
        };


        // $scope.page = 1

        // $rootScope.prodWrapperHeigth

        // $rootScope.getProducts = async () =>{
        //     if ($scope.page<1) { $scope.page=1}
        //     // Check
        //     const height =   $('#product-items').height()
        //     const row = Math.floor(height/132)
        //     const data = [...$rootScope.productList]
        //     const page =   await chunkArray(data, 6*row)

        //     if (page[$scope.page-1]) {
        //         return  page[$scope.page-1]
        //     }
        //     return;

        // }

        $rootScope.selectProduct = (prod) => {
            var totalQuantity = 0;
            var totalAmount = 0;
            var orders = localStorage.getItem("pos_orders")
            orders = JSON.parse(orders)
            var session_selected = localStorage.getItem("pos_session_selected")
            session_selected = JSON.parse(session_selected)
            for (let k = 0; k < orders.length; k++) {
                const ele = orders[k];
                if (ele.id == $rootScope.selected) {
                    if (ele.items.length == 0) {
                        if (!prod.quantity) {
                            prod.quantity = 1
                        }
                        prod.total = prod.quantity * prod.salePrice;
                        ele.items.push(prod);
                        ele.totalQuantity = prod.quantity;
                        ele.totalAmount = prod.total;
                        ele.customerPay = ele.totalAmount;
                    } else {
                        var loop = false;
                        for (let i = 0; i < ele.items.length; i++) {
                            const e = ele.items[i];
                            if (prod.id == e.id) {
                                if (prod.quantity) {
                                    e.quantity += prod.quantity;
                                } else {
                                    e.quantity += 1;
                                }
                                e.total = e.quantity * e.salePrice;
                                loop = true;
                            }
                            totalQuantity += e.quantity;
                            totalAmount += e.total;
                            ele.customerPay = totalAmount;
                        }
                        ele.totalQuantity = totalQuantity;
                        ele.totalAmount = totalAmount;
                        if (!loop) {
                            if (!prod.quantity) {
                                prod.quantity = 1
                            }
                            prod.total = prod.quantity * prod.salePrice;
                            ele.items.push(prod);
                            ele.totalQuantity += 1;
                            ele.totalAmount += prod.total;
                            ele.customerPay = ele.totalAmount;
                        }
                    }
                    $rootScope.total_Quantity = ele.totalQuantity
                    $rootScope.total_Bill = ele.totalAmount
                    $rootScope.customerPay = ele.customerPay
                    $rootScope.orderInfo.payingamountValues = orders[session_selected.sessionIndex].customerPay
                    localStorage.setItem('pos_orders', JSON.stringify(orders))
                    $rootScope.get_product()
                    $rootScope.getDiscount()
                    $rootScope.PayingAmount()
                        // console.log('vao day',orders)
                }
            }
            // console.log('$rootScope.currentCart',$rootScope.currentCart)
            // push_orders(prod)
            // $rootScope.currentCart.push(angular.copy(prod))
            // console.log(tabCtr.get())
        };

        $scope.popOut = false;
        $scope.popOutAttribute = false
        $scope.showCateFilter = () => {
            if (!$scope.popOut) {
                return ($scope.popOut = true)
            }
            return ($scope.popOut = false)
        }
        $scope.showAttrFilter = () => {
            if (!$scope.popOutAttribute) {
                return ($scope.popOutAttribute = true);
            } else {
                return ($scope.popOutAttribute = false);
            }
        };
        $scope.close = () => {
            return ($scope.popOut = false)
        }
        $scope.closeAttr = () => {
            return ($scope.popOutAttribute = false)
        }

        $scope.myClick = function(node) {

            var confirm = dialog.confirm('Editar', node);
            confirm.result.then(function(btn) {

            });
        };

        $scope.setProducts = async() => {
            $scope.prods = await $rootScope.getProducts();
            return;
        };


        //  Common function for controller here
        const chunkArray = (myArray, chunk_size) => {
            var results = [];

            while (myArray.length) {
                results.push(myArray.splice(0, chunk_size));
            }
            return results;
        }

        $scope.nodes = {};
        $scope.categoryFilterId = []
        $http({
            method: "POST",
            url: "/api/category-product",
        }).then(
            (response) => {
                response.data[1].forEach((e) => {
                    $scope.nodes[`category_${e.id}`] = e
                });
            },
            (response) => {}
        )

        $scope.attributeList = []
        $scope.attrFilterId = []
        $http({
            method: "POST",
            url: "/api/product-attribute",
        }).then(
            (response) => {
                $scope.attributeList = response.data
            },
            (response) => {}
        )
        $scope.clearFilter = (value) => {
            if (value == 'attr') {
                $scope.attributeList.forEach((e) => {
                    e.values.forEach((i) => {
                        i.checked = false
                    });
                })
            } else if (value == 'category') {
                angular.forEach($scope.nodes, (e, i) => {
                    e.checked = false
                })
            }
        }
        $scope.getCategory = (categoryID) => {
            $http({
                method: "POST",
                url: "/api/category-product",
                params: {
                    id: categoryID
                },
            }).then(
                (response) => {
                    folder = response.data[0]
                    let text = ``
                    folder.forEach((e) => {
                        text += `<li id="li-${e.id}"><label style="width: 65%;"><input class="tree-checkbox resize-checkbox" type="checkbox" ng-model="nodes.category_${e.id}.checked" ng-change=\'checkChange(nodes.category_${e.id})\' /><span class="text-filter">${e.name}</span></label><span ng-show=${e.hasChildren} class="show-hide" id="span-${e.id}" ng-click="showHide(${e.id})"><i class="fa fa-plus-square"></i></span><ul id="ul-${e.id}" class="hide" ng-if=${e.hasChildren}></ul></li>`
                    });
                    var divElement = angular.element(document.querySelector(`#ul-${categoryID}`));
                    divElement.html(text);
                    $compile(divElement)($scope);
                },
                (response) => {}
            );
        }
        $scope.showHide = (ulId) => {
            $scope.getCategory(ulId)
            var hideThis = document.getElementById(`ul-${ulId}`)
            var showHide = angular.element(hideThis).attr('class')
            angular.element(hideThis).attr('class', (showHide === 'show ng-scope' ? 'hide ng-scope' : 'show ng-scope'))
            $(`#span-${ulId}`).find("i").toggleClass("fa-minus-square fa-plus-square");
            // $(`#ul-${ulId}`).slideToggle(100);
        }
        $scope.showIcon = function(node) {
            $scope.nodes.forEach((n) => {
                if (n.id == node) {
                    if (n.hasChildren) {
                        return true;
                    }
                }
            });

        }
        $scope.getCategory(1)

        /////////////////////////////////////////////////
        /// SELECT ALL CHILDRENS

        function parentCheckChange(item) {
            let category = $scope.nodes
            angular.forEach(category, (e, i) => {
                if (e.parentId == item.id) {
                    e.checked = item.checked
                    if (e.hasChildren) {
                        parentCheckChange(e)
                    }
                }
            })
        }

        function childCheckChange(item, parent) {
            angular.forEach($scope.nodes, (e, i) => {
                if (e.id == parent) {
                    if (!item.checked) {
                        e.checked = false;
                    } else {
                        parent.isChecked = true;
                    }
                    if (e.parentId) {
                        childCheckChange(e, e.parentId);
                    }
                }
            })
        }

        $scope.checkChange = function(node) {
            if (node.id == 1) {
                parentCheckChange(node);
            } else {
                if (node.hasChildren) {
                    parentCheckChange(node);
                }
                childCheckChange(node, node.parentId);
            }
        }
        $scope.applyFilter = () => {
            let categoryId = []
            angular.forEach($scope.nodes, (e, i) => {
                if (e.checked) {
                    categoryId.push(e.id)
                }
            })
            $scope.categoryFilterId = categoryId
            $scope.popOut = false;
        }
        $scope.applyAttrFilter = () => {
            let attrId = []
            angular.forEach($scope.attributeList, (e) => {
                e.values.forEach((i) => {
                    if (i.checked) {
                        attrId.push(i.id)
                    }
                })

            })
            $scope.attrFilterId = attrId
            $scope.popOutAttribute = false
        }

        $rootScope.switchProd = true
        $scope.changeProductView = () => {
            $rootScope.switchProd = !$rootScope.switchProd
        }

        setTimeout($rootScope.getProductList, 800)
            ///////////////////////////////
    },
]);

app.filter('productFilter', function() {
    return function(inputArray, filterIDs) {
        if (filterIDs && filterIDs.length > 0) {
            return inputArray.filter(function(entry) {
                return this.indexOf(entry.catetgoryId) !== -1;
            }, filterIDs);
        } else {
            return inputArray.filter(function(entry) {
                return this;
            }, filterIDs);
        }
    };
});
app.filter('productAttrFilter', function() {
    return function(inputArray, filterIDs) {
        if (filterIDs && filterIDs.length > 0) {
            return inputArray.filter(function(entry) {
                return filterIDs.some(function(i) {
                    return entry.attrvalues.indexOf(i) !== -1
                });
            });
        } else {
            return inputArray.filter(function(entry) {
                return this
            }, filterIDs)
        }
    };
});
app.directive("colorMatches", [
    function() {
        return {
            restrict: "A",
            link: function(scope, element, attrs) {
                scope.$watch(attrs.colorMatches, function(newValue, oldValue) {
                    var dataItemValue = element.data("value");
                    var index = dataItemValue
                        .toLowerCase()
                        .indexOf(newValue.toLowerCase());
                    if (index >= 0) {
                        var index = dataItemValue
                            .toLowerCase()
                            .indexOf(newValue.toLowerCase());
                        var length = newValue.length;
                        var original = dataItemValue.substr(index, length);
                        var newText = dataItemValue.replace(
                            original,
                            "<span class='query-match'>" + original + "</span>"
                        );
                        element.html(newText);
                    } else {
                        element.html(dataItemValue);
                    }
                    return;
                });
            },
        };
    },
]);