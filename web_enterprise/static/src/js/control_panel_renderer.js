odoo.define('web.SearchFacet', function (require) {
    "use strict";
    
    var core = require('web.core');
    var Widget = require('web.Widget');
    
    var _t = core._t;
    
    var SearchFacet = Widget.extend({
        template: 'SearchView.SearchFacet',
        events: _.extend({}, Widget.prototype.events, {
            'click .o_facet_remove': '_onFacetRemove',
            'compositionend': '_onCompositionend',
            'compositionstart': '_onCompositionstart',
            'keydown': '_onKeydown',
        }),
        /**
         * @override
         * @param {Object} facet
         */
        init: function (parent, facet) {
            this._super.apply(this, arguments);
    
            var self = this;
            this.facet = facet;
            this.facetValues = _.map(this.facet.filters, function (filter) {
                return self._getFilterDescription(filter);
            });
            this.separator = this._getSeparator();
            this.icon = this._getIcon();
            this._isComposing = false;
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * Get the correct description according to filter.
         *
         * @private
         * @returns {string}
         */
        _getFilterDescription: function (filter) {
            if (filter.type === 'field') {
                var values = _.pluck(filter.autoCompleteValues, 'label');
                return values.join(_t(' or '));
            }
            var description = filter.description;
            if (filter.hasOptions) {
                if (filter.type === 'filter') {
                    const optionDescriptions = [];
                    const sortFunction = (o1, o2) =>
                        filter.options.findIndex(o => o.optionId === o1) - filter.options.findIndex(o => o.optionId === o2);
                    const p = _.partition([...filter.currentOptionIds], optionId =>
                        filter.options.find(o => o.optionId === optionId).groupId === 1);
                    const yearIds = p[1].sort(sortFunction);
                    const otherOptionIds = p[0].sort(sortFunction);
                    // the following case corresponds to years selected only
                    if (otherOptionIds.length === 0) {
                        yearIds.forEach(yearId => {
                            const d = filter.basicDomains[yearId];
                            optionDescriptions.push(d.description);
                        });
                    } else {
                        otherOptionIds.forEach(optionId => {
                            yearIds.forEach(yearId => {
                                const d = filter.basicDomains[yearId + '__' + optionId];
                                optionDescriptions.push(d.description);
                            });
                        });
                    }
                    description += ': ' + optionDescriptions.join('/');
                } else {
                    description = description += ': ' +
                                    filter.options.find(o => o.optionId === filter.optionId).description;
                }
            }
            if (filter.type === 'timeRange') {
                var timeRangeValue =_.findWhere(filter.timeRangeOptions, {
                    optionId: filter.timeRangeId,
                });
                description += ': ' + timeRangeValue.description;
                if (filter.comparisonTimeRangeId) {
                    var comparisonTimeRangeValue =_.findWhere(filter.comparisonTimeRangeOptions, {
                        optionId: filter.comparisonTimeRangeId,
                    });
                    description += ' / ' + comparisonTimeRangeValue.description;
                }
            }
            return description;
        },
        /**
         * Get the correct icon according to facet type.
         *
         * @private
         * @returns {string}
         */
        _getIcon: function () {
            var icon;
            if (this.facet.type === 'filter') {
                icon = 'fa-filter';
            } else if (this.facet.type === 'groupBy') {
                icon = 'fa-bars';
            } else if (this.facet.type === 'favorite') {
                icon = 'fa-star';
            } else if (this.facet.type === 'timeRange') {
                icon = 'fa-calendar';
            }
            return icon;
        },
        /**
         * Get the correct separator according to facet type.
         *
         * @private
         * @returns {string}
         */
        _getSeparator: function () {
            var separator;
            if (this.facet.type === 'filter') {
                separator = _t('or');
            } else if (this.facet.type === 'field') {
                separator = _t('or');
            } else if (this.facet.type === 'groupBy') {
                separator = '>';
            }
            return separator;
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * @private
         * @param {CompositionEvent} ev
         */
        _onCompositionend: function (ev) {
            this._isComposing = false;
        },
        /**
         * @private
         * @param {CompositionEvent} ev
         */
        _onCompositionstart: function (ev) {
            this._isComposing = true;
        },
        /**
         * @private
         */
        _onFacetRemove: function () {
            this.trigger_up('facet_removed', {group: this.facet});
        },
        /**
         * @private
         * @param {KeyboardEvent} ev
         */
        _onKeydown: function (ev) {
            if (this._isComposing) {
                return;
            }
            switch (ev.which) {
                case $.ui.keyCode.BACKSPACE:
                    this.trigger_up('facet_removed', {group: this.facet});
                    break;
            }
        },
    });
    
    return SearchFacet;
    
    });
    
odoo.define('web.search_bar_autocomplete_sources_registry', function (require) {
    "use strict";
    
    var Registry = require('web.Registry');
    
    return new Registry();
    
    });
odoo.define('web.SearchPanel', function (require) {
    "use strict";
    
    /**
     * This file defines the SearchPanel widget for Kanban. It allows to
     * filter/manage data easily.
     */
    
    var core = require('web.core');
    var Domain = require('web.Domain');
    var pyUtils = require('web.py_utils');
    var viewUtils = require('web.viewUtils');
    var Widget = require('web.Widget');
    
    var qweb = core.qweb;
    
    // defaultViewTypes is the list of view types for which the searchpanel is
    // present by default (if not explicitly stated in the 'view_types' attribute
    // in the arch)
    var defaultViewTypes = ['kanban', 'tree'];
    
    /**
     * Given a <searchpanel> arch node, iterate over its children to generate the
     * description of each section (being either a category or a filter).
     *
     * @param {Object} node a <searchpanel> arch node
     * @param {Object} fields the fields of the model
     * @returns {Object}
     */
    function _processSearchPanelNode(node, fields) {
        var sections = {};
        node.children.forEach((childNode, index) => {
            if (childNode.tag !== 'field') {
                return;
            }
            if (childNode.attrs.invisible === "1") {
                return;
            }
            var fieldName = childNode.attrs.name;
            var type = childNode.attrs.select === 'multi' ? 'filter' : 'category';
    
            var sectionId = _.uniqueId('section_');
            var section = {
                color: childNode.attrs.color,
                description: childNode.attrs.string || fields[fieldName].string,
                fieldName: fieldName,
                icon: childNode.attrs.icon,
                id: sectionId,
                index: index,
                type: type,
            };
            if (section.type === 'category') {
                section.icon = section.icon || 'fa-folder';
            } else if (section.type === 'filter') {
                section.disableCounters = !!pyUtils.py_eval(childNode.attrs.disable_counters || '0');
                section.domain = childNode.attrs.domain || '[]';
                section.groupBy = childNode.attrs.groupby;
                section.icon = section.icon || 'fa-filter';
            }
            sections[sectionId] = section;
        });
        return sections;
    }
    
    var SearchPanel = Widget.extend({
        className: 'o_search_panel',
        events: {
            'click .o_search_panel_category_value header': '_onCategoryValueClicked',
            'click .o_search_panel_category_value .o_toggle_fold': '_onToggleFoldCategory',
            'click .o_search_panel_filter_group .o_toggle_fold': '_onToggleFoldFilterGroup',
            'change .o_search_panel_filter_value > div > input': '_onFilterValueChanged',
            'change .o_search_panel_filter_group > div > input': '_onFilterGroupChanged',
        },
    
        /**
         * @override
         * @param {Object} params
         * @param {Object} [params.defaultValues={}] the value(s) to activate by
         *   default, for each filter and category
         * @param {boolean} [params.defaultNoFilter=false] if true, select 'All' as
         *   value for each category that has no value specified in defaultValues
         *   (instead of looking in the localStorage for the last selected value)
         * @param {Object} params.fields
         * @param {string} params.model
         * @param {Array[]} params.searchDomain domain coming from controlPanel
         * @param {Object} params.sections
         * @param {Object} [params.state] state exported by another searchpanel
         *   instance
         */
        init: function (parent, params) {
            this._super.apply(this, arguments);
    
            this.categories = _.pick(params.sections, function (section) {
                return section.type === 'category';
            });
            this.filters = _.pick(params.sections, function (section) {
                return section.type === 'filter';
            });
    
            this.initialState = params.state;
            this.scrollTop = this.initialState && this.initialState.scrollTop || null;
            this.defaultValues = params.defaultValues || {};
            if (params.defaultNoFilter) {
                Object.keys(this.categories).forEach((categoryId) => {
                    var fieldName = this.categories[categoryId].fieldName;
                    this.defaultValues[fieldName] = this.defaultValues[fieldName] || false;
                });
            }
            this.fields = params.fields;
            this.model = params.model;
            this.className = params.classes.concat(['o_search_panel']).join(' ');
            this.searchDomain = params.searchDomain;
        },
        /**
         * @override
         */
        willStart: function () {
            var self = this;
            var loadCategoriesProm;
            if (this.initialState) {
                this.filters = this.initialState.filters;
                this.categories = this.initialState.categories;
            } else {
                loadCategoriesProm = this._fetchCategories().then(function () {
                    return self._fetchFilters().then(self._applyDefaultFilterValues.bind(self));
                });
            }
            return Promise.all([loadCategoriesProm, this._super.apply(this, arguments)]);
        },
        /**
         * @override
         */
        start: function () {
            this._render();
            return this._super.apply(this, arguments);
        },
        /**
         * Called each time the searchPanel is attached into the DOM.
         */
        on_attach_callback: function () {
            if (this.scrollTop !== null) {
                this.el.scrollTop = this.scrollTop;
            }
        },
    
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
    
        /**
         * Parse a given search view arch to extract the searchpanel information
         * (i.e. a description of each filter/category). Note that according to the
         * 'view_types' attribute on the <searchpanel> node, and the given viewType,
         * it may return undefined, meaning that no searchpanel should be rendered
         * for the current view.
         *
         * Note that this is static method, called by AbstractView, *before*
         * instantiating the SearchPanel, as depending on what it returns, we may
         * or may not instantiate a SearchPanel.
         *
         * @static
         * @params {Object} viewInfo the viewInfo of a search view
         * @params {string} viewInfo.arch
         * @params {Object} viewInfo.fields
         * @params {string} viewType the type of the current view (e.g. 'kanban')
         * @returns {Object|undefined}
         */
        computeSearchPanelParams: function (viewInfo, viewType) {
            var searchPanelSections;
            var classes;
            if (viewInfo) {
                var arch = viewUtils.parseArch(viewInfo.arch);
                viewType = viewType === 'list' ? 'tree' : viewType;
                arch.children.forEach(function (node) {
                    if (node.tag === 'searchpanel') {
                        var attrs = node.attrs;
                        var viewTypes = defaultViewTypes;
                        if (attrs.view_types) {
                            viewTypes = attrs.view_types.split(',');
                        }
                        if (attrs.class) {
                            classes = attrs.class.split(' ');
                        }
                        if (viewTypes.indexOf(viewType) !== -1) {
                            searchPanelSections = _processSearchPanelNode(node, viewInfo.fields);
                        }
                    }
                });
            }
            return {
                sections: searchPanelSections,
                classes: classes,
            };
        },
        /**
         * Export the current state (categories and filters) of the searchpanel.
         *
         * @returns {Object}
         */
        exportState: function () {
            return {
                categories: this.categories,
                filters: this.filters,
                scrollTop: this.el ? this.el.scrollTop : null,
            };
        },
        /**
         * @returns {Array[]} the current searchPanel domain based on active
         *   categories and checked filters
         */
        getDomain: function () {
            return this._getCategoryDomain().concat(this._getFilterDomain());
        },
        /**
         * Import a previously exported state (see exportState).
         *
         * @param {Object} state
         * @param {Object} state.filters.
         * @param {Object} state.categories
         */
        importState: function (state) {
            this.categories = state.categories || this.categories;
            this.filters = state.filters || this.filters;
            this.scrollTop = state.scrollTop;
            this._render();
        },
        /**
         * Reload the filters and re-render. Note that we only reload the filters if
         * the controlPanel domain or searchPanel domain has changed.
         *
         * @param {Object} params
         * @param {Array[]} params.searchDomain domain coming from controlPanel
         * @returns {Promise}
         */
        update: function (params) {
            var currentSearchDomainStr = JSON.stringify(this.searchDomain);
            var newSearchDomainStr = JSON.stringify(params.searchDomain);
            var filtersProm;
            if (this.needReload || (currentSearchDomainStr !== newSearchDomainStr)) {
                this.needReload = false;
                this.searchDomain = params.searchDomain;
                filtersProm = this._fetchFilters();
            }
            return Promise.resolve(filtersProm).then(this._render.bind(this));
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * Set active values for each filter (coming from context). This needs to be
         * done only once, at widget startup.
         *
         * @private
         */
        _applyDefaultFilterValues: function () {
            var self = this;
            Object.keys(this.filters).forEach(function (filterId) {
                var filter = self.filters[filterId];
                var defaultValues = self.defaultValues[filter.fieldName] || [];
                defaultValues.forEach(function (value) {
                    if (filter.values[value]) {
                        filter.values[value].checked = true;
                    }
                });
                Object.keys(filter.groups || []).forEach(function (groupId) {
                    self._updateFilterGroupState(filter.groups[groupId]);
                });
            });
        },
        /**
         * @private
         * @param {string} categoryId
         * @param {Object[]} values
         */
        _createCategoryTree: function (categoryId, values) {
            var category = this.categories[categoryId];
            var parentField = category.parentField;
    
            category.values = {};
            _.each(values, function (value) {
                category.values[value.id] = _.extend({}, value, {
                    childrenIds: [],
                    folded: true,
                    parentId: value[parentField] && value[parentField][0] || false,
                });
            });
            _.map(values, function (value) {
                var value = category.values[value.id];
                var parentCategoryId = value.parentId;
                if (parentCategoryId && parentCategoryId in category.values) {
                    category.values[parentCategoryId].childrenIds.push(value.id);
                }
            });
            category.rootIds = _.filter(_.map(values, function (value) {
                return value.id;
            }), function (valueId) {
                var value = category.values[valueId];
                return value.parentId === false;
            });
    
            // set active value
            var validValues = _.pluck(category.values, 'id').concat([false]);
            var value = this._getCategoryDefaultValue(category, validValues);
            category.activeValueId = _.contains(validValues, value) ? value : false;
    
            // unfold ancestor values of active value to make it is visible
            if (category.activeValueId) {
                var parentValueIds = this._getAncestorValueIds(category, category.activeValueId);
                parentValueIds.forEach(function (parentValue) {
                    category.values[parentValue].folded = false;
                });
            }
        },
        /**
         * @private
         * @param {string} filterId
         * @param {Object[]} values
         */
        _createFilterTree: function (filterId, values) {
            var filter = this.filters[filterId];
    
            // restore checked property
            values.forEach(function (value) {
                var oldValue = filter.values && filter.values[value.id];
                value.checked = oldValue && oldValue.checked || false;
            });
    
            filter.values = {};
            var groupIds = [];
            if (filter.groupBy) {
                var groups = {};
                values.forEach(function (value) {
                    var groupId = value.group_id;
                    if (!groups[groupId]) {
                        if (groupId) {
                            groupIds.push(groupId);
                        }
                        groups[groupId] = {
                            folded: false,
                            id: groupId,
                            name: value.group_name,
                            values: {},
                            tooltip: value.group_tooltip,
                            sequence: value.group_sequence,
                            hex_color: value.group_hex_color,
                            sortedValueIds: [],
                        };
                        // restore former checked and folded state
                        var oldGroup = filter.groups && filter.groups[groupId];
                        groups[groupId].state = oldGroup && oldGroup.state || false;
                        groups[groupId].folded = oldGroup && oldGroup.folded || false;
                    }
                    groups[groupId].values[value.id] = value;
                    groups[groupId].sortedValueIds.push(value.id);
                });
                filter.groups = groups;
                filter.sortedGroupIds = _.sortBy(groupIds, function (groupId) {
                    return groups[groupId].sequence || groups[groupId].name;
                });
                Object.keys(filter.groups).forEach(function (groupId) {
                    filter.values = _.extend(filter.values, filter.groups[groupId].values);
                });
            } else {
                values.forEach(function (value) {
                    filter.values[value.id] = value;
                });
                filter.sortedValueIds = values.map(function (value) {
                    return value.id;
                });
            }
        },
        /**
         * Fetch values for each category. This is done only once, at startup.
         *
         * @private
         * @returns {Promise} resolved when all categories have been fetched
         */
        _fetchCategories: function () {
            var self = this;
            var proms = Object.keys(this.categories).map(function (categoryId) {
                var category = self.categories[categoryId];
                var field = self.fields[category.fieldName];
                var categoriesProm;
                if (field.type === 'selection') {
                    var values = field.selection.map(function (value) {
                        return {id: value[0], display_name: value[1]};
                    });
                    categoriesProm = Promise.resolve(values);
                } else {
                    categoriesProm = self._rpc({
                        method: 'search_panel_select_range',
                        model: self.model,
                        args: [category.fieldName],
                    }).then(function (result) {
                        category.parentField = result.parent_field;
                        return result.values;
                    });
                }
                return categoriesProm.then(function (values) {
                    self._createCategoryTree(categoryId, values);
                });
            });
            return Promise.all(proms);
        },
        /**
         * Fetch values for each filter. This is done at startup, and at each reload
         * (when the controlPanel or searchPanel domain changes).
         *
         * @private
         * @returns {Promise} resolved when all filters have been fetched
         */
        _fetchFilters: function () {
            var self = this;
            var evalContext = {};
            Object.keys(this.categories).forEach(function (categoryId) {
                var category = self.categories[categoryId];
                evalContext[category.fieldName] = category.activeValueId;
            });
            var categoryDomain = this._getCategoryDomain();
            var filterDomain = this._getFilterDomain();
            var proms = Object.keys(this.filters).map(function (filterId) {
                var filter = self.filters[filterId];
                return self._rpc({
                    method: 'search_panel_select_multi_range',
                    model: self.model,
                    args: [filter.fieldName],
                    kwargs: {
                        category_domain: categoryDomain,
                        comodel_domain: Domain.prototype.stringToArray(filter.domain, evalContext),
                        disable_counters: filter.disableCounters,
                        filter_domain: filterDomain,
                        group_by: filter.groupBy || false,
                        search_domain: self.searchDomain,
                    },
                }).then(function (values) {
                    self._createFilterTree(filterId, values);
                });
            });
            return Promise.all(proms);
        },
        /**
         * @private
         * @param {Object} category
         * @param {Array} validValues
         * @returns id of the default item of the category or false
         */
        _getCategoryDefaultValue: function (category, validValues) {
            // set active value from context
            var value = this.defaultValues[category.fieldName];
            // if not set in context, or set to an unknown value, set active value
            // from localStorage
            if (!_.contains(validValues, value)) {
                var storageKey = this._getLocalStorageKey(category);
                return this.call('local_storage', 'getItem', storageKey);
            }
            return value;
        },
        /**
         * Compute and return the domain based on the current active categories.
         *
         * @private
         * @returns {Array[]}
         */
        _getCategoryDomain: function () {
            var self = this;
    
            function categoryToDomain(domain, categoryId) {
                var category = self.categories[categoryId];
                if (category.activeValueId) {
                    var field = self.fields[category.fieldName];
                    var op = (field.type === 'many2one' && category.parentField) ? 'child_of' : '=';
                    domain.push([category.fieldName, op, category.activeValueId]);
                }
                return domain;
            }
    
            return Object.keys(this.categories).reduce(categoryToDomain, []);
        },
        /**
         * Compute and return the domain based on the current checked filters.
         * The values of a single filter are combined using a simple rule: checked values within
         * a same group are combined with an 'OR' (this is expressed as single condition using a list)
         * and groups are combined with an 'AND' (expressed by concatenation of conditions).
         * If a filter has no groups, its checked values are implicitely considered as forming
         * a group (and grouped using an 'OR').
         *
         * @private
         * @returns {Array[]}
         */
        _getFilterDomain: function () {
            var self = this;
    
            function getCheckedValueIds(values) {
                return Object.keys(values).reduce(function (checkedValues, valueId) {
                    if (values[valueId].checked) {
                        checkedValues.push(values[valueId].id);
                    }
                    return checkedValues;
                }, []);
            }
    
            function filterToDomain(domain, filterId) {
                var filter = self.filters[filterId];
                if (filter.groups) {
                    Object.keys(filter.groups).forEach(function (groupId) {
                        var group = filter.groups[groupId];
                        var checkedValues = getCheckedValueIds(group.values);
                        if (checkedValues.length) {
                            domain.push([filter.fieldName, 'in', checkedValues]);
                        }
                    });
                } else if (filter.values) {
                    var checkedValues = getCheckedValueIds(filter.values);
                    if (checkedValues.length) {
                        domain.push([filter.fieldName, 'in', checkedValues]);
                    }
                }
                return domain;
            }
    
            return Object.keys(this.filters).reduce(filterToDomain, []);
        },
        /**
         * The active id of each category is stored in the localStorage, s.t. it
         * can be restored afterwards (when the action is reloaded, for instance).
         * This function returns the key in the sessionStorage for a given category.
         *
         * @param {Object} category
         * @returns {string}
         */
        _getLocalStorageKey: function (category) {
            return 'searchpanel_' + this.model + '_' + category.fieldName;
        },
        /**
         * @private
         * @param {Object} category
         * @param {integer} categoryValueId
         * @returns {integer[]} list of ids of the ancestors of the given value in
         *   the given category
         */
        _getAncestorValueIds: function (category, categoryValueId) {
            var categoryValue = category.values[categoryValueId];
            var parentId = categoryValue.parentId;
            if (parentId) {
                return [parentId].concat(this._getAncestorValueIds(category, parentId));
            }
            return [];
        },
        /**
         * Compute the current searchPanel domain based on categories and filters,
         * and notify environment of the domain change.
         *
         * Note that this assumes that the environment will update the searchPanel.
         * This is done as such to ensure the coordination between the reloading of
         * the searchPanel and the reloading of the data.
         *
         * @private
         */
        _notifyDomainUpdated: function () {
            this.needReload = true;
            this.trigger_up('search_panel_domain_updated', {
                domain: this.getDomain(),
            });
        },
        /**
         * @private
         */
        _render: function () {
            var self = this;
            this.$el.empty();
    
            // sort categories and filters according to their index
            var categories = Object.keys(this.categories).map(function (categoryId) {
                return self.categories[categoryId];
            });
            var filters = Object.keys(this.filters).map(function (filterId) {
                return self.filters[filterId];
            });
            var sections = categories.concat(filters).sort(function (s1, s2) {
                return s1.index - s2.index;
            });
    
            sections.forEach(function (section) {
                if (Object.keys(section.values).length) {
                    if (section.type === 'category') {
                        self.$el.append(self._renderCategory(section));
                    } else {
                        self.$el.append(self._renderFilter(section));
                    }
                }
            });
        },
        /**
         * @private
         * @param {Object} category
         * @returns {string}
         */
        _renderCategory: function (category) {
            return qweb.render('SearchPanel.Category', {category: category});
        },
        /**
         * @private
         * @param {Object} filter
         * @returns {jQuery}
         */
        _renderFilter: function (filter) {
            var $filter = $(qweb.render('SearchPanel.Filter', {filter: filter}));
    
            // set group inputs in indeterminate state when necessary
            Object.keys(filter.groups || {}).forEach(function (groupId) {
                var state = filter.groups[groupId].state;
                // group 'false' is not displayed
                if (groupId !== 'false' && state === 'indeterminate') {
                    $filter
                        .find('.o_search_panel_filter_group[data-group-id=' + groupId + '] input')
                        .get(0)
                        .indeterminate = true;
                }
            });
    
            return $filter;
        },
        /**
         * Updates the state property of a given filter's group according to the
         * checked property of its values.
         *
         * @private
         * @param {Object} group
         */
        _updateFilterGroupState: function (group) {
            var valuePartition = _.partition(Object.keys(group.values), function (valueId) {
                return group.values[valueId].checked;
            });
            if (valuePartition[0].length && valuePartition[1].length) {
                group.state = 'indeterminate';
            } else if (valuePartition[0].length) {
                group.state = 'checked';
            } else {
                group.state = 'unchecked';
            }
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onCategoryValueClicked: function (ev) {
            ev.stopPropagation();
            var $item = $(ev.currentTarget).closest('.o_search_panel_category_value');
            var category = this.categories[$item.data('categoryId')];
            var valueId = $item.data('id') || false;
            category.activeValueId = valueId;
            if (category.values[valueId]) {
                category.values[valueId].folded = !category.values[valueId].folded;
            }
            var storageKey = this._getLocalStorageKey(category);
            this.call('local_storage', 'setItem', storageKey, valueId);
            this._notifyDomainUpdated();
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onFilterGroupChanged: function (ev) {
            ev.stopPropagation();
            var $item = $(ev.target).closest('.o_search_panel_filter_group');
            var filter = this.filters[$item.data('filterId')];
            var groupId = $item.data('groupId');
            var group = filter.groups[groupId];
            group.state = group.state === 'checked' ? 'unchecked' : 'checked';
            Object.keys(group.values).forEach(function (valueId) {
                group.values[valueId].checked = group.state === 'checked';
            });
            this._notifyDomainUpdated();
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onFilterValueChanged: function (ev) {
            ev.stopPropagation();
            var $item = $(ev.target).closest('.o_search_panel_filter_value');
            var valueId = $item.data('valueId');
            var filter = this.filters[$item.data('filterId')];
            var value = filter.values[valueId];
            value.checked = !value.checked;
            var group = filter.groups && filter.groups[value.group_id];
            if (group) {
                this._updateFilterGroupState(group);
            }
            this._notifyDomainUpdated();
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onToggleFoldCategory: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $item = $(ev.currentTarget).closest('.o_search_panel_category_value');
            var category = this.categories[$item.data('categoryId')];
            var valueId = $item.data('id');
            category.values[valueId].folded = !category.values[valueId].folded;
            this._render();
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onToggleFoldFilterGroup: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $item = $(ev.currentTarget).closest('.o_search_panel_filter_group');
            var filter = this.filters[$item.data('filterId')];
            var groupId = $item.data('groupId');
            filter.groups[groupId].folded = !filter.groups[groupId].folded;
            this._render();
        },
    });
    
    return SearchPanel;
    
    });
    
odoo.define('web.SearchBar', function (require) {
    "use strict";
    
    var AutoComplete = require('web.AutoComplete');
    var searchBarAutocompleteRegistry = require('web.search_bar_autocomplete_sources_registry');
    var SearchFacet = require('web.SearchFacet');
    var Widget = require('web.Widget');
    
    var SearchBar = Widget.extend({
        template: 'SearchView.SearchBar',
        events: _.extend({}, Widget.prototype.events, {
            'compositionend .o_searchview_input': '_onCompositionendInput',
            'compositionstart .o_searchview_input': '_onCompositionstartInput',
            'keydown': '_onKeydown',
        }),
        /**
         * @override
         * @param {Object} [params]
         * @param {Object} [params.context]
         * @param {Object[]} [params.facets]
         * @param {Object} [params.fields]
         * @param {Object[]} [params.filterFields]
         * @param {Object[]} [params.filters]
         * @param {Object[]} [params.groupBys]
         */
        init: function (parent, params) {
            this._super.apply(this, arguments);
    
            this.context = params.context;
    
            this.facets = params.facets;
            this.fields = params.fields;
            this.filterFields = params.filterFields;
    
            this.autoCompleteSources = [];
            this.searchFacets = [];
            this._isInputComposing = false;
        },
        /**
         * @override
         */
        start: function () {
            this.$input = this.$('input');
            var self = this;
            var defs = [this._super.apply(this, arguments)];
            _.each(this.facets, function (facet) {
                defs.push(self._renderFacet(facet));
            });
            defs.push(this._setupAutoCompletion());
            return Promise.all(defs);
        },
    
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
    
        /**
         * Focus the searchbar.
         */
        focus: function () {
          this.$input.focus();
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * @private
         */
        _focusFollowing: function () {
            var focusedIndex = this._getFocusedFacetIndex();
            var $toFocus;
            if (focusedIndex === this.searchFacets.length - 1) {
                $toFocus = this.$input;
            } else {
                $toFocus = this.searchFacets.length && this.searchFacets[focusedIndex + 1].$el;
            }
    
            if ($toFocus.length) {
                $toFocus.focus();
            }
        },
        /**
         * @private
         */
        _focusPreceding: function () {
            var focusedIndex = this._getFocusedFacetIndex();
            var $toFocus;
            if (focusedIndex === -1) {
                $toFocus = this.searchFacets.length && _.last(this.searchFacets).$el;
            } else if (focusedIndex === 0) {
                $toFocus = this.$input;
            } else {
                $toFocus = this.searchFacets.length && this.searchFacets[focusedIndex - 1].$el;
            }
    
            if ($toFocus.length) {
                $toFocus.focus();
            }
        },
        /**
         * @private
         * @returns {integer}
         */
        _getFocusedFacetIndex: function () {
            return _.findIndex(this.searchFacets, function (searchFacet) {
                return searchFacet.$el[0] === document.activeElement;
            });
        },
        /**
         * Provide auto-completion result for req.term.
         *
         * @private
         * @param {Object} req request to complete
         * @param {String} req.term searched term to complete
         * @param {Function} callback
         */
        _getAutoCompleteSources: function (req, callback) {
            var defs = this.autoCompleteSources.map(function (source) {
                return source.getAutocompletionValues(req.term);
            });
            Promise.all(defs).then(function (result) {
                var resultCleaned = _(result).chain()
                    .compact()
                    .flatten(true)
                    .value();
                callback(resultCleaned);
            });
        },
        /**
         * @private
         * @param {Object} facet
         * @returns {Promise}
         */
        _renderFacet: function (facet) {
            var searchFacet = new SearchFacet(this, facet);
            this.searchFacets.push(searchFacet);
            return searchFacet.insertBefore(this.$('input'));
        },
        /**
         * @private
         * @returns {Promise}
         */
        _setupAutoCompletion: function () {
            var self = this;
            this._setupAutoCompletionWidgets();
            this.autoComplete = new AutoComplete(this, {
                $input: this.$('input'),
                source: this._getAutoCompleteSources.bind(this),
                select: this._onAutoCompleteSelected.bind(this),
                get_search_string: function () {
                    return self.$input.val().trim();
                },
            });
            return this.autoComplete.appendTo(this.$el);
        },
        /**
         * @private
         */
        _setupAutoCompletionWidgets: function () {
            var self = this;
            var registry = searchBarAutocompleteRegistry;
            _.each(this.filterFields, function (filter) {
                var field = self.fields[filter.attrs.name];
                var Obj = registry.getAny([filter.attrs.widget, field.type]);
                if (Obj) {
                    self.autoCompleteSources.push(new (Obj) (self, filter, field, self.context));
                }
            });
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * @private
         * @param {Event} e
         * @param {Object} ui
         * @param {Object} ui.item selected completion item
         */
        _onAutoCompleteSelected: function (e, ui) {
            e.preventDefault();
            var facet = ui.item.facet;
            if (!facet) {
                // this happens when selecting "(no result)" item
                this.trigger_up('reset');
                return;
            }
            var filter = facet.filter;
            if (filter.type === 'field') {
                var values = filter.autoCompleteValues;
                values.push(facet.values[0]);
                this.trigger_up('autocompletion_filter', {
                    filterId: filter.id,
                    autoCompleteValues: values,
                });
            } else {
                this.trigger_up('autocompletion_filter', {
                    filterId: filter.id,
                });
            }
        },
        /**
         * @rivate
         * @param {CompositionEvent} ev
         */
        _onCompositionendInput: function () {
            this._isInputComposing = false;
        },
        /**
         * @rivate
         * @param {CompositionEvent} ev
         */
        _onCompositionstartInput: function () {
            this._isInputComposing = true;
        },
        /**
         * @private
         * @param {KeyEvent} e
         */
        _onKeydown: function (e) {
            if (this._isInputComposing) {
                return;
            }
            switch(e.which) {
                case $.ui.keyCode.LEFT:
                    this._focusPreceding();
                    e.preventDefault();
                    break;
                case $.ui.keyCode.RIGHT:
                    this._focusFollowing();
                    e.preventDefault();
                    break;
                case $.ui.keyCode.DOWN:
                    // if the searchbar dropdown is closed, try to focus the renderer
                    const $dropdown = this.$('.o_searchview_autocomplete:visible');
                    if (!$dropdown.length) {
                        this.trigger_up('navigation_move', { direction: 'down' });
                        e.preventDefault();
                    }
                    break;
                case $.ui.keyCode.BACKSPACE:
                    if (this.$input.val() === '') {
                        this.trigger_up('facet_removed');
                    }
                    break;
                case $.ui.keyCode.ENTER:
                    if (this.$input.val() === '') {
                        this.trigger_up('reload');
                    }
                    break;
            }
        },
    });
    
    return SearchBar;
    
    });
    
odoo.define('web.mvc', function (require) {
    "use strict";
    
    /**
     * This file contains a 'formalization' of a MVC pattern, applied to Odoo
     * idioms.
     *
     * For a simple widget/component, this is definitely overkill.  However, when
     * working on complex systems, such as Odoo views (or the control panel, or some
     * client actions), it is useful to clearly separate the code in concerns.
     *
     * We define here 4 classes: Factory, Model, Renderer, Controller.  Note that
     * for various historical reasons, we use the term Renderer instead of View. The
     * main issue is that the term 'View' is used way too much in Odoo land, and
     * adding it would increase the confusion.
     *
     * In short, here are the responsabilities of the four classes:
     * - Model: this is where the main state of the system lives.  This is the part
     *     that will talk to the server, process the results and is the owner of the
     *     state
     * - Renderer: this is the UI code: it should only be concerned with the look
     *     and feel of the system: rendering, binding handlers, ...
     * - Controller: coordinates the model with the renderer and the parents widgets.
     *     This is more a 'plumbing' widget.
     * - Factory: setting up the MRC components is a complex task, because each of
     *     them needs the proper arguments/options, it needs to be extensible, they
     *     needs to be created in the proper order, ...  The job of the factory is
     *     to process all the various arguments, and make sure each component is as
     *     simple as possible.
     */
    
    var ajax = require('web.ajax');
    var Class = require('web.Class');
    var mixins = require('web.mixins');
    var ServicesMixin = require('web.ServicesMixin');
    var Widget = require('web.Widget');
    
    
    /**
     * Owner of the state, this component is tasked with fetching data, processing
     * it, updating it, ...
     *
     * Note that this is not a widget: it is a class which has not UI representation.
     *
     * @class Model
     */
    var Model = Class.extend(mixins.EventDispatcherMixin, ServicesMixin, {
        /**
         * @param {Widget} parent
         * @param {Object} params
         */
        init: function (parent, params) {
            mixins.EventDispatcherMixin.init.call(this);
            this.setParent(parent);
        },
    
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
    
        /**
         * This method should return the complete state necessary for the renderer
         * to display the current data.
         *
         * @returns {*}
         */
        get: function () {
        },
        /**
         * The load method is called once in a model, when we load the data for the
         * first time.  The method returns (a promise that resolves to) some kind
         * of token/handle.  The handle can then be used with the get method to
         * access a representation of the data.
         *
         * @param {Object} params
         * @returns {Promise} The promise resolves to some kind of handle
         */
        load: function () {
            return Promise.resolve();
        },
    });
    
    /**
     * Only responsability of this component is to display the user interface, and
     * react to user changes.
     *
     * @class Renderer
     */
    var Renderer = Widget.extend({
        /**
         * @override
         * @param {any} state
         * @param {Object} params
         */
        init: function (parent, state, params) {
            this._super(parent);
            this.state = state;
        },
    });
    
    /**
     * The controller has to coordinate between parent, renderer and model.
     *
     * @class Controller
     */
    var Controller = Widget.extend({
        /**
         * @override
         * @param {Model} model
         * @param {Renderer} renderer
         * @param {Object} params
         */
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.model = model;
            this.renderer = renderer;
        },
        /**
         * @returns {Promise}
         */
        start: function () {
            return Promise.all(
                [this._super.apply(this, arguments),
                this._startRenderer()]
            );
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * Appends the renderer in the $el. To override to insert it elsewhere.
         *
         * @private
         */
        _startRenderer: function () {
            return this.renderer.appendTo(this.$el);
        },
    });
    
    var Factory = Class.extend({
        config: {
            Model: Model,
            Renderer: Renderer,
            Controller: Controller,
        },
        /**
         * @override
         */
        init: function () {
            this.rendererParams = {};
            this.controllerParams = {};
            this.modelParams = {};
            this.loadParams = {};
        },
    
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
    
        /**
         * Main method of the Factory class. Create a controller, and make sure that
         * data and libraries are loaded.
         *
         * There is a unusual thing going in this method with parents: we create
         * renderer/model with parent as parent, then we have to reassign them at
         * the end to make sure that we have the proper relationships.  This is
         * necessary to solve the problem that the controller needs the model and
         * the renderer to be instantiated, but the model need a parent to be able
         * to load itself, and the renderer needs the data in its constructor.
         *
         * @param {Widget} parent the parent of the resulting Controller (most
         *      likely an action manager)
         * @returns {Promise<Controller>}
         */
        getController: function (parent) {
            var self = this;
            var model = this.getModel(parent);
            return Promise.all([this._loadData(model), ajax.loadLibs(this)]).then(function (result) {
                var state = result[0];
                var renderer = self.getRenderer(parent, state);
                var Controller = self.Controller || self.config.Controller;
                var controllerParams = _.extend({
                    initialState: state,
                }, self.controllerParams);
                var controller = new Controller(parent, model, renderer, controllerParams);
                model.setParent(controller);
                renderer.setParent(controller);
                return controller;
            });
        },
        /**
         * Returns a new model instance
         *
         * @param {Widget} parent the parent of the model
         * @returns {Model} instance of the model
         */
        getModel: function (parent) {
            var Model = this.config.Model;
            return new Model(parent, this.modelParams);
        },
        /**
         * Returns a new renderer instance
         *
         * @param {Widget} parent the parent of the renderer
         * @param {Object} state the information related to the rendered data
         * @returns {Renderer} instance of the renderer
         */
        getRenderer: function (parent, state) {
            var Renderer = this.config.Renderer;
            return new Renderer(parent, state, this.rendererParams);
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * Loads initial data from the model
         *
         * @private
         * @param {Model} model a Model instance
         * @returns {Promise<*>} a promise that resolves to the value returned by
         *   the get method from the model
         * @todo: get rid of loadParams (use modelParams instead)
         */
        _loadData: function (model) {
            return model.load(this.loadParams).then(function () {
                return model.get.apply(model, arguments);
            });
        },
    });
    
    
    return {
        Factory: Factory,
        Model: Model,
        Renderer: Renderer,
        Controller: Controller,
    };
    
    });
    
odoo.define('web.FilterMenu', function (require) {
    "use strict";
    
    var config = require('web.config');
    var core = require('web.core');
    var Domain = require('web.Domain');
    var DropdownMenu = require('web.DropdownMenu');
    var search_filters = require('web.search_filters');
    
    var _t = core._t;
    var QWeb = core.qweb;
    
    var FilterMenu = DropdownMenu.extend({
        custom_events: {
            confirm_proposition: '_onConfirmProposition',
            remove_proposition: '_onRemoveProposition',
        },
        events: _.extend({}, DropdownMenu.prototype.events, {
            'click .o_add_custom_filter': '_onAddCustomFilterClick',
            'click .o_add_condition': '_onAddCondition',
            'click .o_apply_filter': '_onApplyClick',
        }),
        /**
         * @override
         * @param {Object} fields
         */
        init: function (parent, filters, fields) {
            this._super(parent, filters);
    
            // determines where the filter menu is displayed and its style
            this.isMobile = config.device.isMobile;
            // determines when the 'Add custom filter' submenu is open
            this.generatorMenuIsOpen = false;
            this.propositions = [];
            this.fields = _.pick(fields, function (field, name) {
                return field.selectable !== false && name !== 'id';
            });
            this.fields.id = {string: 'ID', type: 'id', searchable: true};
            this.dropdownCategory = 'filter';
            this.dropdownTitle = _t('Filters');
            this.dropdownIcon = 'fa fa-filter';
            this.dropdownSymbol = this.isMobile ?
                                    'fa fa-chevron-right float-right mt4' :
                                    false;
            this.dropdownStyle.mainButton.class = 'o_filters_menu_button ' +
                                                    this.dropdownStyle.mainButton.class;
        },
        /**
         * Render the template used to add a new custom filter and append it
         * to the basic dropdown menu.
         *
         * @override
         */
        start: function () {
            var superProm = this._super.apply(this, arguments);
            this.$menu.addClass('o_filters_menu');
            this._renderGeneratorMenu();
            return superProm;
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * Add a proposition inside the custom filter edition menu.
         *
         * @private
         * @returns {Promise}
         */
        _appendProposition: function () {
            // make modern sear_filters code!!! It works but...
            var prop = new search_filters.ExtendedSearchProposition(this, this.fields);
            this.propositions.push(prop);
            this.$('.o_apply_filter').prop('disabled', false);
            return prop.insertBefore(this.$addFilterMenu);
        },
        /**
         * Confirm a filter proposition, creates it and add it to the menu.
         *
         * @private
         */
        _commitSearch: function () {
            var filters = _.invoke(this.propositions, 'get_filter').map(function (preFilter) {
                return {
                    type: 'filter',
                    description: preFilter.attrs.string,
                    domain: Domain.prototype.arrayToString(preFilter.attrs.domain),
                };
            });
            this.trigger_up('new_filters', {filters: filters});
            _.invoke(this.propositions, 'destroy');
            this.propositions = [];
            this._toggleCustomFilterMenu();
        },
        /**
         * @private
         */
        _renderGeneratorMenu: function () {
            this.$el.find('.o_generator_menu').remove();
            if (!this.generatorMenuIsOpen) {
                _.invoke(this.propositions, 'destroy');
                this.propositions = [];
            }
            var $generatorMenu = QWeb.render('FilterMenuGenerator', {widget: this});
            this.$menu.append($generatorMenu);
            this.$addFilterMenu = this.$menu.find('.o_add_filter_menu');
            if (this.generatorMenuIsOpen && !this.propositions.length) {
                this._appendProposition();
            }
            this.$dropdownReference.dropdown('update');
        },
        /**
         * Hide and display the submenu which allows adding custom filters.
         *
         * @private
         */
        _toggleCustomFilterMenu: function () {
            this.generatorMenuIsOpen = !this.generatorMenuIsOpen;
            this._renderGeneratorMenu();
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onAddCondition: function (ev) {
            ev.stopPropagation();
            this._appendProposition();
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onAddCustomFilterClick: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this._toggleCustomFilterMenu();
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onApplyClick: function (ev) {
            ev.stopPropagation();
            this._commitSearch();
        },
        /**
         * @override
         * @private
         * @param {jQueryEvent} ev
         */
        _onBootstrapClose: function () {
            this._super.apply(this, arguments);
            this.generatorMenuIsOpen = false;
            this._renderGeneratorMenu();
        },
        /**
         * @private
         * @param {OdooEvent} ev
         */
        _onConfirmProposition: function (ev) {
            ev.stopPropagation();
            this._commitSearch();
        },
        /**
         * @private
         * @param {OdooEvent} ev
         */
        _onRemoveProposition: function (ev) {
            ev.stopPropagation();
            this.propositions = _.without(this.propositions, ev.target);
            if (!this.propositions.length) {
                this.$('.o_apply_filter').prop('disabled', true);
            }
            ev.target.destroy();
        },
    });
    
    return FilterMenu;
    
    });
    
odoo.define('web.ControlPanelRenderer', function (require) {
    "use strict";
    
    var config = require('web.config');
    var data = require('web.data');
    var FavoriteMenu = require('web.FavoriteMenu');
    var FilterMenu = require('web.FilterMenu');
    var GroupByMenu = require('web.GroupByMenu');
    var mvc = require('web.mvc');
    var SearchBar = require('web.SearchBar');
    var TimeRangeMenu = require('web.TimeRangeMenu');
    
    var Renderer = mvc.Renderer;
    
    var ControlPanelRenderer = Renderer.extend({
        template: 'ControlPanel',
        custom_events: {
            get_action_info: '_onGetActionInfo',
        },
        events: _.extend({}, Renderer.prototype.events, {
            'click .o_searchview_more': '_onMore',
        }),
    
        /**
         * @override
         * @param {Object} [params.action] current action if any
         * @param {Object} [params.context]
         * @param {Object[]} [params.breadcrumbs=[]] list of breadcrumbs elements
         * @param {boolean} [params.withBreadcrumbs=false] if false, breadcrumbs
         *   won't be rendered
         * @param {boolean} [params.withSearchBar=false] if false, no search bar
         *   is rendered
         * @param {string[]} [params.searchMenuTypes=[]] determines the search menus
         *   that are displayed.
         * @param {String} [params.template] the QWeb template to render the
         *   ControlPanel. By default, the template 'ControlPanel' will be used.
         * @param {string} [params.title=''] the title visible in control panel
         */
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this._breadcrumbs = params.breadcrumbs || [];
            this._title = params.title || '';
            this.withBreadcrumbs = params.withBreadcrumbs;
            this.withSearchBar = params.withSearchBar;
            if (params.template) {
                this.template = params.template;
            }
            this.context = params.context;
    
            this.$subMenus = null;
            this.action = params.action;
            this.displaySearchMenu = true;
            this.isMobile = config.device.isMobile;
            this.menusSetup = false;
            this.searchMenuTypes = params.searchMenuTypes || [];
            this.subMenus = {};
        },
        /**
         * Render the control panel and create a dictionnary of its exposed elements.
         *
         * @override
         */
        start: function () {
            var self = this;
    
            // exposed jQuery nodesets
            this.nodes = {
                $buttons: this.$('.o_cp_buttons'),
                $pager: this.$('.o_cp_pager'),
                $sidebar: this.$('.o_cp_sidebar'),
                $switch_buttons: this.$('.o_cp_switch_buttons'),
            };
    
            // if we don't use the default search bar and buttons, we expose the
            // corresponding areas for custom content
            if (!this.withSearchBar) {
                this.nodes.$searchview = this.$('.o_cp_searchview');
            }
            if (this.searchMenuTypes.length === 0) {
                this.nodes.$searchview_buttons = this.$('.o_search_options');
            }
    
            if (this.withBreadcrumbs) {
                this._renderBreadcrumbs();
            }
    
            var superDef = this._super.apply(this, arguments);
            var searchDef = this._renderSearch();
            return Promise.all([superDef, searchDef]).then(function () {
                self._setSearchMenusVisibility();
            });
        },
        /**
         * @override
         */
        on_attach_callback: function () {
            this._focusSearchInput();
        },
        /**
         * @override
         */
        on_detach_callback: function () {
        },
    
        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------
    
        /**
         * @returns {Object|undefined}
         */
        getLastFacet: function () {
            return this.state.facets.slice(-1)[0];
        },
        /**
         * This function is called when actions call 'updateControlPanel' with
         * custom contents to insert in the exposed areas.
         *
         * @param {Object} status
         * @param {Object} [status.cp_content] dictionnary containing the jQuery
         *   elements to insert in the exposed areas
         * @param {string} [status.breadcrumbs] the breadcrumbs to display before
         *   the current controller
         * @param {string} [status.title] the title of the current controller, to
         *   display at the end of the breadcrumbs
         * @param {Object} [options]
         * @param {Boolean} [options.clear=true] set to false to keep control panel
         *   elements that are not in status.cp_content (useful for partial updates)
         */
        updateContents: function (status, options) {
            var new_cp_content = status.cp_content || {};
            var clear = 'clear' in (options || {}) ? options.clear : true;
    
            if (this.withBreadcrumbs) {
                this._breadcrumbs = status.breadcrumbs || this._breadcrumbs;
                this._title = status.title || this._title;
                this._renderBreadcrumbs();
            }
    
            if (clear) {
                this._detachContent(this.nodes);
            } else {
                this._detachContent(_.pick(this.nodes, _.keys(new_cp_content)));
            }
            this._attachContent(new_cp_content);
        },
        /**
         * Update the state of the renderer state. It retriggers a full rerendering.
         *
         * @param {Object} state
         * @returns {Promise}
         */
        updateState: function (state) {
            this.state = state;
            return this._renderSearch();
        },
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * @private
         * @param {Object} content dictionnary of jQuery elements to attach, whose
         *   keys are jQuery nodes identifiers in this.nodes
         */
        _attachContent: function (content) {
            for (var $element in content) {
                var $nodeset = content[$element];
                if ($nodeset && this.nodes[$element]) {
                    this.nodes[$element].append($nodeset);
                }
            }
        },
        /**
         * @private
         * @param {Object} content subset of this.nodes to detach
         */
        _detachContent: function (content) {
            for (var $element in content) {
                content[$element].contents().detach();
            }
        },
        /**
         * @private
         */
        _focusSearchInput: function () {
            if (this.withSearchBar && !config.device.isMobile) {
                // in mobile mode, we would rather not focus manually the
                // input, because it opens up the integrated keyboard, which is
                // not what you expect when you just selected a filter.
                this.searchBar.focus();
            }
        },
        /**
         * @private
         * @param {string} menuType
         * @returns {Objects[]} menuItems
         */
        _getMenuItems: function (menuType) {
            var menuItems;
            if (menuType === 'filter') {
                menuItems = this.state.filters;
            }
            if (menuType === 'groupBy') {
                menuItems = this.state.groupBys;
            }
            if (menuType === 'timeRange') {
                menuItems = this.state.timeRanges;
            }
            if (menuType === 'favorite') {
                menuItems = this.state.favorites;
            }
            return menuItems;
        },
        /**
         * @private
         * @returns {jQueryElement}
         */
        _getSubMenusPlace: function () {
            return $('<div>').appendTo(this.$('.o_search_options'));
        },
        /**
         * @private
         */
        _renderBreadcrumbs: function () {
            var self = this;
            var breadcrumbsDescriptors = this._breadcrumbs.concat({title: this._title});
            var breadcrumbs = breadcrumbsDescriptors.map(function (bc, index) {
                return self._renderBreadcrumbsItem(bc, index, breadcrumbsDescriptors.length);
            });
            this.$('.breadcrumb').html(breadcrumbs);
        },
        /**
         * Render a breadcrumbs' li jQuery element.
         *
         * @private
         * @param {Object} bc
         * @param {string} bc.title
         * @param {string} bc.controllerID
         * @param {integer} index
         * @param {integer} length
         * @returns {jQueryElement} $bc
         */
        _renderBreadcrumbsItem: function (bc, index, length) {
            var self = this;
            var is_last = (index === length-1);
            var li_content = bc.title && _.escape(bc.title.trim()) || data.noDisplayContent;
            var $bc = $('<li>', {class: 'breadcrumb-item'})
                .append(is_last ? li_content : $('<a>', {href: '#'}).html(li_content))
                .toggleClass('active', is_last);
            if (!is_last) {
                $bc.click(function (ev) {
                    ev.preventDefault();
                    self.trigger_up('breadcrumb_clicked', {controllerID: bc.controllerID});
                });
            }
    
            var secondLast = index === length - 2;
            if (secondLast) {
                $bc.attr('accessKey', 'b');
            }
    
            return $bc;
        },
        /**
         * Renderer the search bar and the search menus
         *
         * @private
         * @returns {Promise}
         */
        _renderSearch: function () {
            var defs = [];
            if (this.menusSetup) {
                this._updateMenus();
            } else {
                this.menusSetup = true;
                defs = defs.concat(this._setupMenus());
            }
            if (this.withSearchBar) {
                defs.push(this._renderSearchBar());
            }
            return Promise.all(defs).then(this._focusSearchInput.bind(this));
        },
        /**
         * @private
         * @returns {Promise}
         */
        _renderSearchBar: function () {
            // TODO: might need a reload instead of a destroy/instantiate
            var oldSearchBar = this.searchBar;
            this.searchBar = new SearchBar(this, {
                context: this.context,
                facets: this.state.facets,
                fields: this.state.fields,
                filterFields: this.state.filterFields,
            });
            return this.searchBar.appendTo(this.$('.o_searchview')).then(function () {
                if (oldSearchBar) {
                    oldSearchBar.destroy();
                }
            });
        },
        /**
         * Hide or show the search menus according to this.displaySearchMenu.
         *
         * @private
         */
        _setSearchMenusVisibility: function () {
            this.$('.o_searchview_more')
                .toggleClass('fa-search-plus', !this.displaySearchMenu)
                .toggleClass('fa-search-minus', this.displaySearchMenu);
            this.$('.o_search_options')
                .toggleClass('o_hidden', !this.displaySearchMenu);
        },
        /**
         * Create a new menu of the given type and append it to this.$subMenus.
         * This menu is also added to this.subMenus.
         *
         * @private
         * @param {string} menuType
         * @returns {Promise}
         */
        _setupMenu: function (menuType) {
            var Menu;
            var menu;
            if (menuType === 'filter') {
                Menu = FilterMenu;
            }
            if (menuType === 'groupBy') {
                Menu = GroupByMenu;
            }
            if (menuType === 'timeRange') {
                Menu = TimeRangeMenu;
            }
            if (menuType === 'favorite') {
                Menu = FavoriteMenu;
            }
            if (_.contains(['filter', 'groupBy', 'timeRange'], menuType)) {
                menu = new Menu(this, this._getMenuItems(menuType), this.state.fields);
            }
            if (menuType === 'favorite') {
                menu = new Menu(this, this._getMenuItems(menuType), this.action);
            }
            this.subMenus[menuType] = menu;
            return menu.appendTo(this.$subMenus);
        },
        /**
         * Instantiate the search menu determined by this.searchMenuTypes.
         *
         * @private
         * @returns {Promise[]}
         */
        _setupMenus: function () {
            this.$subMenus = this._getSubMenusPlace();
            return this.searchMenuTypes.map(this._setupMenu.bind(this));
        },
        /**
         * Update the search menus.
         *
         * @private
         */
        _updateMenus: function () {
            var self = this;
            this.searchMenuTypes.forEach(function (menuType) {
                self.subMenus[menuType].update(self._getMenuItems(menuType));
            });
        },
    
        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
    
        /**
         * Toggle the search menus visibility.
         *
         * @private
         */
        _onMore: function () {
            this.displaySearchMenu = !this.displaySearchMenu;
            this._setSearchMenusVisibility();
        },
    });
    
    return ControlPanelRenderer;
    
    });
    
odoo.define('web_enterprise.ControlPanelRenderer', function (require) {
"use strict";

var config = require('web.config');
var ControlPanelRenderer = require('web.ControlPanelRenderer');

ControlPanelRenderer.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _renderBreadcrumbsItem: function (bc, index, length) {
        var $bc = this._super.apply(this, arguments);

        var isLast = (index === length-1);
        var isBeforeLast = (index === length-2);

        $bc.toggleClass('d-none d-md-inline-block', !isLast && !isBeforeLast)
           .toggleClass('o_back_button', isBeforeLast)
           .toggleClass('btn btn-secondary', isBeforeLast && config.device.isMobile);

        return $bc;
    },
});

});
