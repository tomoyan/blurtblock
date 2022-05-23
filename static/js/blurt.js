$(document).ready(function(){
    let BLURTURL = 'https://blurt.blog'
    let BLURTBLOCK = 'https://blurtblock.herokuapp.com';
    let IMGBASE = 'https://imgp.blurt.world/profileimage';
    let BLURTWALLET = 'https://blocks.blurtwallet.com';

    $("#nav-delegation-tab").click(function(){
        // incoming delegation
        $.ajax(document.delegationApiIn,
        {
            dataType: 'json', // type of response data
            timeout: 60000,     // timeout milliseconds
            success: function (data, status, xhr) {
                var liStr = ``;
                if (jQuery.isEmptyObject(data['incoming'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Incoming Delegation</span></li>`;
                    $("#incomingResult").html(liStr);
                }
                else {
                   $("#incomingResult").empty();
                   $.each(data['incoming'], function(index, value){
                        liStr = `
                            <li class="list-group-item" data-field=>

                            <div class="container">
                              <div class="row">
                                <div class="col-sm">
                                    <span><img src="${IMGBASE}/${value.delegator}"
                                            alt="profile_image"
                                            class="img-thumbnail rounded-circle float-left mr-3"
                                            width="64">
                                    </span>
                                    <span>
                                        <a class="text-blurt font-weight-bold mr-3"
                                            href="https://blurt.blog/@${value.delegator}"
                                            target="_blank" rel="noopener noreferrer">
                                            ${value.delegator}</a>
                                        <br>
                                        <a class="text-blurt font-weight-bold mr-3"
                                            href="https://blurtblock.herokuapp.com/${value.delegator}"
                                            target="_blank" rel="noopener noreferrer">
                                            Profile</a>
                                    </span>
                                </div>
                                <div class="col-sm">
                                    <span class="font-weight-bold">${value.bp} BP</span>
                                </div>
                              </div>
                            </div>

                            </li>`;

                        $("#incomingResult").append(liStr);
                    });
               }
            },
        });

        // outgoing elegation
        $.ajax(document.delegationApiOut,
        {
            dataType: 'json', // type of response data
            timeout: 60000,     // timeout milliseconds
            success: function (data, status, xhr) {
                var liStr = ``;
                if (jQuery.isEmptyObject(data['outgoing'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Outgoing Delegation</span></li>`;
                    $("#outgoingResult").html(liStr);
                }
                else {
                   $("#outgoingResult").empty();
                   $.each(data['outgoing'], function(index, value){
                        liStr = `
                            <li class="list-group-item" data-field=>

                            <div class="container">
                              <div class="row">
                                <div class="col-sm">
                                    <span><img src="${IMGBASE}/${value.delegatee}"
                                            alt="profile_image"
                                            class="img-thumbnail rounded-circle float-left mr-3"
                                            width="64">
                                    </span>
                                    <span>
                                        <a class="text-blurt font-weight-bold mr-3"
                                            href="https://blurt.blog/@${value.delegatee}"
                                            target="_blank" rel="noopener noreferrer">
                                            ${value.delegatee}</a>
                                        <br>
                                        <a class="text-blurt font-weight-bold mr-3"
                                            href="https://blurtblock.herokuapp.com/${value.delegatee}"
                                            target="_blank" rel="noopener noreferrer">
                                            Profile</a>
                                    </span>
                                </div>
                                <div class="col-sm">
                                    <span class="font-weight-bold">${value.bp} BP</span>
                                </div>
                              </div>
                            </div>

                            </li>`;

                        $("#outgoingResult").append(liStr);
                    });
               }
            },
        });

        // expiring elegation
        $.ajax(document.delegationApiExp,
        {
            dataType: 'json', // type of response data
            timeout: 60000,     // timeout milliseconds
            success: function (data, status, xhr) {
                var liStr = ``;
                if (jQuery.isEmptyObject(data['expiring'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Expiring Delegation</span></li>`;
                    $("#expiringResult").html(liStr);
                }
                else {
                   $("#expiringResult").empty();
                   $.each(data['expiring'], function(index, value){
                        liStr = `
                            <li class="list-group-item" data-field=>

                            <div class="container">
                              <div class="row">
                                <div class="col-sm">
                                    <span class="font-weight-bold">${value.bp} BP</span><br>
                                </div>
                                <div class="col-sm">
                                    <span class="font-weight-bold">${value.expiration}</span>
                                </div>
                              </div>
                            </div>

                            </li>`;

                        $("#expiringResult").append(liStr);
                    });
               }
            },
        });
    });

    $("#rewardHistory").click(function(){
        let heading = `
        <li class="list-group-item">
            <div class="container">
                <div class="row">
                    <div class="col-sm text-sm-left text-truncate">
                        <strong>Duration</strong>
                    </div>
                    <div class="col-sm text-sm-left text-truncate">
                        <strong>Author BP</strong>
                    </div>
                    <div class="col-sm text-sm-left text-truncate">
                        <strong>Curation BP</strong>
                    </div>
                    <div class="col-sm text-sm-left text-truncate">
                    <strong>Total BP</strong>
                    </div>
                </div>
            </div>
        </li>
        <li  class="list-group-item">
            <div id="oneDayResult">
                <div class="container">
                    <div class="row">
                        <div class="col-sm text-sm-left text-truncate">
                            Last 24 Hours
                        </div>
                        <div class="col-sm text-sm-left text-truncate">
                            <div class="spinner-border spinner-border-sm text-blurt"
                                role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </li>
        <li  class="list-group-item">
            <div id="sevenDayResult">
                <div class="container">
                    <div class="row">
                        <div class="col-sm text-sm-left text-truncate">
                            Last 7 Days
                        </div>
                        <div class="col-sm text-sm-left text-truncate">
                            <div class="spinner-border spinner-border-sm text-blurt"
                                role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </li>
        <li  class="list-group-item">
            <div id="thirtyDayResult">
                <div class="container">
                    <div class="row">
                        <div class="col-sm text-sm-left text-truncate">
                            Last 30 Days
                        </div>
                        <div class="col-sm text-sm-left text-truncate">
                            <div class="spinner-border spinner-border-sm text-blurt"
                                role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </li>`;
        $("#historyResult").html(heading);

        // 1 day reward
        $.ajax(document.rewardOneApi,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            success: function (data, status, xhr) {
                let transactions = ``

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data)) {
                    transactions = `<li class="list-group-item">No Reward Data</li>`;
                    $("#oneDayResult").html(transactions);
                }
                else {
                    let producer = ``
                    if ( parseFloat(data['producer']) ) {
                        producer = `(${data['producer']} BP)`;
                    }
                    transactions = `
                        <div class="container">
                            <div class="row">
                                <div class="col-sm text-sm-left text-truncate">
                                    Last 24 Hours
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['author']} BP
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['curation']} BP
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['total']} BP <br>
                                    ${producer}
                                </div>
                            </div>
                        </div>`;
                    $("#oneDayResult").html(transactions);
                }
            },
            error: function (jqXhr, textStatus, errorMessage) {
                $("#oneDayResult").html('Oops! ' + errorMessage + ' Please reload');
            }
        });
        // 7 day reward
        $.ajax(document.rewardSevenApi,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            success: function (data, status, xhr) {
                let transactions = ``

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data)) {
                    transactions = `<li class="list-group-item">No Reward Data</li>`;
                    $("#sevenDayResult").html(transactions);
                }
                else {
                    let producer = ``
                    if ( parseFloat(data['producer']) ) {
                        producer = `(${data['producer']} BP)`;
                    }
                    transactions = `
                        <div class="container">
                            <div class="row">
                                <div class="col-sm text-sm-left text-truncate">
                                    Last 7 Days
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['author']} BP
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['curation']} BP
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['total']} BP <br>
                                    ${producer}
                                </div>
                            </div>
                        </div>`;
                    $("#sevenDayResult").html(transactions);
                }
            },
            error: function (jqXhr, textStatus, errorMessage) {
                $("#sevenDayResult").html('Oops! ' + errorMessage + ' Please reload');
            }
        });
        // 30 day reward
        $.ajax(document.rewardThirtyApi,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            success: function (data, status, xhr) {
                let transactions = ``

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data)) {
                    transactions = `<li class="list-group-item">No Reward Data</li>`;
                    $("#thirtyDayResult").html(transactions);
                }
                else {
                    let producer = ``
                    if ( parseFloat(data['producer']) ) {
                        producer = `(${data['producer']} BP)`;
                    }
                    transactions = `
                        <div class="container">
                            <div class="row">
                                <div class="col-sm text-sm-left text-truncate">
                                    Last 30 Days
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['author']} BP
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['curation']} BP
                                </div>
                                <div class="col-sm text-sm-left text-truncate">
                                    ${data['total']} BP <br>
                                    ${producer}
                                </div>
                            </div>
                        </div>`;
                    $("#thirtyDayResult").html(transactions);
                }
            },
            error: function (jqXhr, textStatus, errorMessage) {
                $("#thirtyDayResult").html('Oops! ' + errorMessage + ' Please reload');
            }
        });
    });

    $("#followHistory").click(function(){
        // follow history
        $.ajax(document.followerApi,
        {
            // type of response data
            dataType: 'json',
            // 30 sec timeout in milliseconds
            timeout: 30000,
            success: function (data, status, xhr) {
                let transaction = ``;
                // clear out the result html
                $("#historyResult").html(transaction);

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data)) {
                    transaction = `<li class="list-group-item">No Follow Data</li>`;
                    $("#historyResult").html(transaction);
                }
                else {
                    $.each(data, function(key, value){
                        let follow = ``;
                        if (value) {
                            follow = `
                                <span class="badge badge-blurt font-weight-light">
                                    Following</span>`;
                        }
                        transaction = `
                        <li class="list-group-item">
                            <div class="container">
                                <div class="row">
                                    <div class="col-sm text-sm-left text-truncate">
                                        <img src="${IMGBASE}/${key}"
                                                alt="profile_image"
                                                class="img-thumbnail rounded-circle float-left mr-3"
                                                width="64">
                                        <a class="text-blurt font-weight-bold mr-3"
                                            href="${BLURTBLOCK}/${key}"
                                            target="_blank" rel="noopener noreferrer">${key}
                                        </a><br>
                                        ${follow}
                                    </div>
                                </div>
                            </div>
                        </li>`
                        $("#historyResult").append(transaction);
                    });
                }
            },
            error: function (jqXhr, textStatus, errorMessage) {
                $("#historySpinners").addClass('invisible');
                $("#historyResult").html('Oops! ' + errorMessage + ' Please try again later');
            }
        });
    });

    $("#followingHistory").click(function(){
        // following history
        $.ajax(document.followingApi,
        {
            // type of response data
            dataType: 'json',
            // 30 sec timeout in milliseconds
            timeout: 30000,
            success: function (data, status, xhr) {
                let transaction = ``
                // clear out the result html
                $("#historyResult").html(transaction);

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data)) {
                    transaction = `<li class="list-group-item">No Following Data</li>`;
                    $("#historyResult").html(transaction);
                }
                else {
                    $.each(data, function(key, value){
                        let follow = ``;
                        if (value) {
                            follow = `
                                <span class="badge badge-blurt font-weight-light">
                                    Following you</span>`;
                        }
                        transaction = `
                        <li class="list-group-item">
                            <div class="container">
                                <div class="row">
                                    <div class="col-sm text-sm-left text-truncate">
                                        <img src="${IMGBASE}/${key}"
                                                alt="profile_image"
                                                class="img-thumbnail rounded-circle float-left mr-3"
                                                width="64">
                                        <a class="text-blurt font-weight-bold mr-3"
                                            href="${BLURTBLOCK}/${key}"
                                            target="_blank" rel="noopener noreferrer">${key}
                                        </a><br>
                                        ${follow}
                                    </div>
                                </div>
                            </div>
                        </li>`
                        $("#historyResult").append(transaction);
                    });
                }
            },
            error: function (jqXhr, textStatus, errorMessage) {
                $("#historySpinners").addClass('invisible');
                $("#historyResult").html('Oops! ' + errorMessage + ' Please try again later');
            }
        });
    });

    $("#muteHistory").click(function(){
        // mute history
        $.ajax(document.muteApi,
        {
            // type of response data
            dataType: 'json', // type of response data
            // 30 sec timeout in milliseconds
            timeout: 30000,
            success: function (data, status, xhr) {
                let transaction = `<li class="list-group-item text-blurt h3">
                    Muted by Users</li>`;
                $("#historyResult").html(transaction);

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data['muter'])) {
                    transaction = `<li class="list-group-item">No Mute Data</li>`;
                    $("#historyResult").append(transaction);
                }
                else {
                    $.each(data['muter'], function(key, value){
                        transaction = `
                        <li class="list-group-item">
                            <div class="container">
                                <div class="row">
                                    <div class="col-sm text-sm-left text-truncate">
                                        <img src="${IMGBASE}/${value}"
                                                alt="profile_image"
                                                class="img-thumbnail rounded-circle float-left mr-3"
                                                width="64">
                                        <a class="text-blurt font-weight-bold mr-3"
                                            href="${BLURTBLOCK}/${value}"
                                            target="_blank" rel="noopener noreferrer">${value}
                                        </a><br>
                                    </div>
                                </div>
                            </div>
                        </li>`
                        $("#historyResult").append(transaction);
                    });
                }
                transaction = `<li class="list-group-item text-blurt h3">
                    Muted Users</li>`;
                $("#historyResult").append(transaction);
                if (jQuery.isEmptyObject(data['muting'])) {
                    transaction = `<li class="list-group-item">No Muting Data</li>`;
                    $("#historyResult").append(transaction);
                }
                else {
                    $.each(data['muting'], function(key, value){
                        transaction = `
                        <li class="list-group-item">
                            <div class="container">
                                <div class="row">
                                    <div class="col-sm text-sm-left text-truncate">
                                        <img src="${IMGBASE}/${value}"
                                                alt="profile_image"
                                                class="img-thumbnail rounded-circle float-left mr-3"
                                                width="64">
                                        <a class="text-blurt font-weight-bold mr-3"
                                            href="${BLURTBLOCK}/${value}"
                                            target="_blank" rel="noopener noreferrer">${value}
                                        </a><br>
                                    </div>
                                </div>
                            </div>
                        </li>`
                        $("#historyResult").append(transaction);
                    });
                }
            },
            error: function (jqXhr, textStatus, errorMessage) {
                $("#historySpinners").addClass('invisible');
                $("#historyResult").html('Oops! ' + errorMessage + ' Please try again later');
            }
        });
    });

    $("#nav-history-tab, #operationHistory").click(function(){
        $("#historySpinners").removeClass('invisible');
        $("#historySpinners").addClass('visible');

        // operation history
        $.ajax(document.operationHistoryApi,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            tryCount : 0,
            retryLimit : 3, // retry times
            success: function (data, status, xhr) {
                let transactions = ``

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data)) {
                    transactions = `<li class="list-group-item">No Operation Data</li>`;
                    $("#historyResult").html(transactions);
                }
                else {
                    $("#historyResult").html("");
                    $.each(data, function(index, value){
                        // console.log(index, value);
                        let curation_reward = ``;
                        if (value['type'] === 'curation_reward') {
                            curation_reward = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    ${value['bp']} BP
                                </div>
                                <div class="col-sm-2 text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['comment_author']}/${value['comment_permlink']}"
                                        target="_blank">
                                        ${value['comment_permlink']}
                                    </a>
                                </div>
                            `;
                        }

                        let author_reward = ``;
                        if (value['type'] === 'author_reward') {
                            author_reward = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    ${value['bp']} BP ${value['blurt']} BLURT
                                </div>
                                <div class="col-sm-2 text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['author']}/${value['permlink']}"
                                        target="_blank">
                                        ${value['permlink']}
                                    </a>
                                </div>
                            `;
                        }

                        let producer_reward = ``;
                        if (value['type'] === 'producer_reward') {
                            producer_reward = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    ${value['bp']} BP
                                </div>
                            `;
                        }

                        let comment_benefactor_reward = ``;
                        if (value['type'] === 'comment_benefactor_reward') {
                            comment_benefactor_reward = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    ${value['bp']} BP ${value['blurt']} BLURT
                                </div>
                                <div class="col-sm-2 text-sm-left text-truncate">
                                    ${value['benefactor']} ${value['permlink']}
                                </div>
                            `;
                        }

                        let transfer = ``;
                        if (value['type'] === 'transfer') {
                            transfer = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['from']}"
                                        target="_blank">
                                        ${value['from']}
                                    </a>
                                    <i class="bi bi-arrow-right"></i>
                                    <a href="${BLURTURL}/@${value['to']}"
                                        target="_blank">
                                        ${value['to']}
                                    </a>
                                    ${value['blurt']} BLURT
                                </div>
                            `;
                        }

                        let delegate_vesting_shares = ``;
                        if (value['type'] === 'delegate_vesting_shares') {
                            delegate_vesting_shares = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['from']}"
                                        target="_blank">
                                        ${value['from']}
                                    </a>
                                    <i class="bi bi-arrow-right"></i>
                                    <a href="${BLURTURL}/@${value['to']}"
                                        target="_blank">
                                        ${value['to']}
                                    </a>
                                    ${value['bp']} BP
                                </div>
                            `;
                        }

                        let transfer_to_vesting = ``;
                        if (value['type'] === 'transfer_to_vesting') {
                            transfer_to_vesting = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['from']}"
                                        target="_blank">
                                        ${value['from']}
                                    </a>
                                    <i class="bi bi-arrow-right"></i>
                                    <a href="${BLURTURL}/@${value['to']}"
                                        target="_blank">
                                        ${value['to']}
                                    </a>
                                    ${value['bp']} BP
                                </div>
                            `;
                        }

                        let withdraw_vesting = ``;
                        if (value['type'] === 'withdraw_vesting') {
                            withdraw_vesting = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    Power Down ${value['bp']} BP
                                </div>
                            `;
                        }

                        let claim_reward_balance = ``;
                        if (value['type'] === 'claim_reward_balance') {
                            claim_reward_balance = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    ${value['bp']} BP ${value['blurt']} BLURT
                                </div>
                            `;
                        }

                        let vote = ``;
                        if (value['type'] === 'vote') {
                            vote = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['from']}"
                                        target="_blank">
                                        ${value['from']}
                                    </a>
                                    <i class="bi bi-arrow-right"></i>
                                    <a href="${BLURTURL}/@${value['to']}"
                                        target="_blank">
                                        ${value['to']}
                                    </a>
                                    ${value['weight']} %
                                </div>
                                <div class="col-sm-2 text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['to']}/${value['permlink']}"
                                        target="_blank">
                                        ${value['permlink']}
                                    </a>
                                </div>
                            `;
                        }

                        let comment = ``;
                        if (value['type'] === 'comment') {
                            comment = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['from']}"
                                        target="_blank">
                                        ${value['from']}
                                    </a>
                                    <i class="bi bi-arrow-right"></i>
                                    <a href="${BLURTURL}/@${value['to']}"
                                        target="_blank">
                                        ${value['to']}
                                    </a>
                                </div>
                                <div class="col-sm-2 text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['from']}/${value['permlink']}"
                                        target="_blank">
                                        ${value['permlink']}
                                    </a>
                                </div>
                            `;
                        }

                        let delete_comment = ``;
                        if (value['type'] === 'delete_comment') {
                            delete_comment = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    ${value['permlink']}
                                </div>
                            `;
                        }

                        let witness = ``;
                        if (value['type'] === 'account_witness_vote') {
                            witness = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['account']}"
                                        target="_blank">
                                        ${value['account']}
                                    </a>
                                    <i class="bi bi-arrow-right"></i>
                                    <a href="${BLURTURL}/@${value['witness']}"
                                        target="_blank">
                                        ${value['witness']}
                                    </a>
                                    ${value['approve']}
                                </div>
                            `;
                        }

                        let proxy = ``;
                        if (value['type'] === 'account_witness_proxy') {
                            // console.log(value);
                            proxy = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    <i class="bi bi-arrow-right"></i>
                                    <a href="${BLURTURL}/@${value['proxy']}"
                                        target="_blank">
                                        ${value['proxy']}
                                    </a>
                                </div>
                            `;
                        }

                        let follow = ``;
                        if (value['type'] === 'follow' || value['type'] === 'unfollow') {
                            follow = `
                                <div class="col-sm-auto text-sm-left text-truncate">
                                    <a href="${BLURTURL}/@${value['to']}"
                                        target="_blank">
                                        ${value['to']}
                                    </a>
                                </div>
                            `;
                        }

                        let id = ``;
                        if ( Number.isNaN(value['id'] * 1) ) {
                            id = `
                                <div class="col-sm-1 text-sm-left text-truncate">
                                    <a href="${BLURTWALLET}/?#/tx/${value['id']}"
                                        target="_blank">
                                        ${value['id']}
                                    </a>
                                </div>
                            `;
                        }

                        tx = `
                        <li class="list-group-item">
                            <div class="container">
                                <div class="row">
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        ${value['timestamp']}
                                    </div>
                                    <div class="col-sm-auto text-sm-left
                                        text-truncate font-weight-bolder">
                                        ${value['title']}
                                    </div>
                                    ${curation_reward}
                                    ${author_reward}
                                    ${producer_reward}
                                    ${comment_benefactor_reward}
                                    ${transfer}
                                    ${delegate_vesting_shares}
                                    ${transfer_to_vesting}
                                    ${withdraw_vesting}
                                    ${claim_reward_balance}
                                    ${vote}
                                    ${comment}
                                    ${delete_comment}
                                    ${witness}
                                    ${proxy}
                                    ${follow}
                                    ${id}
                                </div>
                            </div>
                        </li>`;
                        $("#historyResult").append(tx);
                    });
                }
            },
            error: function (jqXhr, textStatus, errorMessage) {
                if (textStatus == 'timeout') {
                    this.tryCount++;
                    if (this.tryCount < this.retryLimit) {
                        //retry
                        $.ajax(this);
                        return;
                    }
                }
                $("#historySpinners").addClass('invisible');
                $("#historyResult").html('Oops! ' + errorMessage + ' Please reload');
            }
        });
    });

    // $("#postHistory").click(function(){
    //     // post history
    //     $.ajax(document.postHistoryApi,
    //     {
    //         dataType: 'json', // type of response data
    //         timeout: 60000, // 60 sec timeout in milliseconds
    //         success: function (data, status, xhr) {
    //         },
    //         error: function (jqXhr, textStatus, errorMessage) {
    //             $("#historyResult").html('Oops! ' + errorMessage + ' Please reload');
    //         }
    //     });
    // });

    // display spinners when history buttons clicked
    $("#rewardHistory").click(function(){
        $("#historySpinners").removeClass('invisible');
        $("#historySpinners").addClass('visible');
    });

    $("#transferHistory").click(function(){
        $("#historySpinners").removeClass('invisible');
        $("#historySpinners").addClass('visible');
    });

    $("#upvoteHistory").click(function(){
        $("#historySpinners").removeClass('invisible');
        $("#historySpinners").addClass('visible');
    });

    $("#commentHistory").click(function(){
        $("#historySpinners").removeClass('invisible');
        $("#historySpinners").addClass('visible');
    });

    $("#followHistory").click(function(){
        $("#historySpinners").removeClass('invisible');
        $("#historySpinners").addClass('visible');
    });

    $("#followingHistory").click(function(){
        $("#historySpinners").removeClass('invisible');
        $("#historySpinners").addClass('visible');
    });

    $("#muteHistory").click(function(){
        $("#historySpinners").removeClass('invisible');
        $("#historySpinners").addClass('visible');
    });
});
