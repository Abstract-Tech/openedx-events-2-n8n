'use strict';
(function() {
    var FIELDS_BY_AUTH_TYPE = {
        basic: ['basic_auth_username', 'basic_auth_password'],
        header: ['header_auth_name', 'header_auth_value'],
        jwt: ['jwt_auth_secret'],
    };
    var ALL_AUTH_FIELDS = Object.keys(FIELDS_BY_AUTH_TYPE).reduce(function(acc, key) {
        return acc.concat(FIELDS_BY_AUTH_TYPE[key]);
    }, []);

    function toggleAuthFields() {
        var select = document.getElementById('id_auth_type');
        if (!select) {
            return;
        }
        var visibleFields = FIELDS_BY_AUTH_TYPE[select.value] || [];
        ALL_AUTH_FIELDS.forEach(function(fieldName) {
            var row = document.querySelector('.field-' + fieldName);
            if (row) {
                row.style.display = visibleFields.includes(fieldName) ? '' : 'none';
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        var select = document.getElementById('id_auth_type');
        if (!select) {
            return;
        }
        select.addEventListener('change', toggleAuthFields);
        toggleAuthFields();
    });
})();
