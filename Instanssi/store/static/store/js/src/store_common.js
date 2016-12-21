/**
 * Assorted common code for the Instanssi store.
 * @todo Move some of this into a sitewide library?
 */

import Vue from 'vue';

// Support for this was still a bit patchy last I checked.
let toLocaleStringSupportsOptions = !!(typeof Intl === 'object'
    && Intl && typeof Intl.NumberFormat === 'function');

function formatPriceLocaleString(price) {
    return price.toLocaleString('fi', { style: 'currency', currency: 'EUR'});
}
function formatPriceLegacy(price) {
    return price.toFixed(2) + ' €';
}
let formatPrice;
if(toLocaleStringSupportsOptions) {
    formatPrice = formatPriceLocaleString;
} else {
    formatPrice = formatPriceLegacy;
}

/**
 * Perform an asynchronous HTTP request to a specific method and path,
 * optionally passing some data (not supported for GET requests).
 * @param {string} method - HTTP method, e.g. 'GET'
 * @param {string} path - URL or path to request
 * @param {Object} [data] - Data to pass in the request (encoded into JSON)
 * @returns {Promise.Object} - Result
 */
function storeXHR(method, path, data) {
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.onload = function () {
            if(xhr.status >= 200 && xhr.status < 300) {
                // tolerate empty response (technically, 204 no content should be used...)
                let response = xhr.responseText;
                resolve((response && response.length) ? JSON.parse(xhr.responseText) : null);
            } else {
                xhr.onerror();
            }
        };
        xhr.onerror = function () {
            reject(xhr.responseText ? JSON.parse(xhr.responseText) : null);
        };
        xhr.open(method, path);
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(data ? JSON.stringify(data) : null);
    });
}

/**
 * Form group with a title, input field and any messages concerning the field.
 */
let storeFormGroup = Vue.component('store-form-group', {
    props: {
        title: String,
        field: String,
        // type: String,
        messages: Object,
        update: Function,
        data: Object,
        required: Boolean,
        /** Chrome-friendly autocomplete hint */
        autocomplete: String
    },
    methods: {
        onInput($event) {
            this.$emit('update', this.field, $event);
        }
    },
    computed: {
        clazz() {
            let { messages, field } = this;
            let className = this.required ? 'form-group form-group-required' : 'form-group';
            if(messages && messages[field] && messages[field].length > 0) {
                return className + ' has-error';
            }
            return className;
        }
    },
    template: `<div v-bind:class="clazz">
        <label class="col-sm-4 control-label">{{ title }}</label>
        <div class="col-sm-8">
            <input class="form-control"
                @input="onInput"
                :autocomplete="autocomplete"
                :id="'store-' + field"
                :value="data[field]"/>
            <store-messages :field="field" :messages="messages" />
        </div>
    </div>`
});

/**
 * Shows messages addressed to a specific named field.
 */
let storeMessages = Vue.component('store-messages', {
    props: {
        /** Field name to pick up messages for. */
        field: String,
        /** Object like { fieldName: [message1, ...] }. */
        messages: Object
    },
    computed: {
        localMessages() {
            let { messages, field } = this;
            if(messages && messages[field] && messages[field].length > 0) {
                let fieldMessages = [];

                // certain exceptions may produce more interesting field messages than others
                messages[field].forEach((msg) => {
                    if (typeof msg === 'string') {
                        fieldMessages.push(msg);
                    } else if(typeof msg === 'object') {
                        // the transaction items serializer produces an embedded errors array
                        // let's just flatten it for now
                        let nonFieldErrors = msg.non_field_errors;
                        if(typeof nonFieldErrors === 'object' && nonFieldErrors.length) {
                            nonFieldErrors.forEach((nfe) => {
                                fieldMessages.push(nfe);
                            })
                        }
                    }
                });
                return fieldMessages;
            }
            return null;
        }
    },
    template: `<div v-show="localMessages"><p>
        <div class="alert alert-danger" role="alert" v-for="message in localMessages">
            <span class="fa fa-times"></span> {{ message }}
        </div>
    </p></div>`
});

let loadingOverlay = Vue.component('loading-overlay', {
    props: {
        loading: Boolean,
        text: String,
    },
    computed: {
        clazz() {
            return this.loading ? 'loading-overlay loading-overlay-active' : 'loading-overlay';
        }
    },
    template: `<div v-bind:class="clazz">
        <div class="fa fa-spinner fa-pulse fa-3x fa-fw"></div>
        <div v-if="text">{{ text }}</div>
    </div>`
});

export { formatPrice, storeXHR, storeFormGroup, storeMessages, loadingOverlay };
