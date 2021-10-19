$(document).ready(function(){
    let BLURTURL = 'https://blurtter.com'
    let BLURTBLOCK = 'https://blurtblock.herokuapp.com';
    let IMGBASE = 'https://imgp.blurt.world/profileimage';
    // let IMGBASE = 'https://cdn.steemitimages.com';
    // let IMGBASE = 'https://images.blurt.blog';

    $("#nav-delegation-tab").click(function(){
        let incomingmessage = `
        <li class="list-group-item" data-field=><span>Not Implemented</span></li>`;
        $("#incomingResult").html(incomingmessage);

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

    $("#transferHistory").click(function(){
        // transfer history
        $.ajax(document.transferHistoryApi,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            tryCount : 0,
            retryLimit : 3, // retry times
            success: function (data, status, xhr) {
                let transactions = ``

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data['history'])) {
                    transactions = `<li class="list-group-item">No Transfer Data</li>`;
                    $("#historyResult").html(transactions);
                }
                else {
                    $("#historyResult").html("");
                    $.each(data['history'], function(index, value){
                        tx = `
                        <li class="list-group-item">
                            <div class="container">
                                <div class="row">
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        ${value['timestamp']}
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        ${value['amount']}
                                        <a class="text-blurt"
                                            href="${BLURTBLOCK}/${value['from']}"
                                            target="_blank" rel="noopener noreferrer">${value['from']}
                                        </a>
                                        to
                                        <a class="text-blurt"
                                            href="${BLURTBLOCK}/${value['to']}"
                                            target="_blank" rel="noopener noreferrer">${value['to']}
                                        </a>
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate"
                                        style="max-width: 450px;">
                                        ${value['memo']}
                                    </div>
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

    $("#upvoteHistory").click(function(){
        // upvote history
        $.ajax(document.upvoteHistoryApi,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            tryCount : 0,
            retryLimit : 3, // retry times
            success: function (data, status, xhr) {
                let transactions = ``

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data['history'])) {
                    transactions = `<li class="list-group-item">No Upvote Data</li>`;
                    $("#historyResult").html(transactions);
                }
                else {
                    $("#historyResult").html("");
                    $.each(data['history'], function(index, value){
                        tx = `
                        <li class="list-group-item">
                            <div class="container">
                                <div class="row">
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        ${value['timestamp']}
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        <a class="text-blurt"
                                            href="${BLURTBLOCK}/${value['voter']}"
                                            target="_blank" rel="noopener noreferrer">${value['voter']}
                                        </a>
                                        voted
                                        <a class="text-blurt"
                                            href="${BLURTBLOCK}/${value['author']}"
                                            target="_blank" rel="noopener noreferrer">${value['author']}
                                        </a>
                                        (${value['weight']}%)
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate"
                                        style="max-width: 500px;">
                                        <a class="text-blurt"
                                            href="${BLURTURL}/@${value['author']}/${value['permlink']}"
                                            target="_blank" rel="noopener noreferrer">${value['permlink']}
                                        </a>
                                    </div>
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

    $("#commentHistory").click(function(){
        // comment history
        $.ajax(document.commentHistoryApi,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            tryCount : 0,
            retryLimit : 3, // retry times
            success: function (data, status, xhr) {
                let transactions = ``

                $("#historySpinners").addClass('invisible');
                if (jQuery.isEmptyObject(data['history'])) {
                    transactions = `<li class="list-group-item">No Comment Data</li>`;
                    $("#historyResult").html(transactions);
                }
                else {
                    $("#historyResult").html("");
                    $.each(data['history'], function(index, value){
                        tx = `
                        <li class="list-group-item">
                            <div class="container">
                                <div class="row">
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        ${value['timestamp']}
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        <a class="text-blurt"
                                            href="${BLURTBLOCK}/${value['author']}"
                                            target="_blank" rel="noopener noreferrer">${value['author']}
                                        </a>
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        ${value['body']}
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate"
                                        style="max-width: 500px;">
                                        <a class="text-blurt"
                                            href="${BLURTURL}/@${value['author']}/${value['permlink']}"
                                            target="_blank" rel="noopener noreferrer">${value['permlink']}
                                        </a>
                                    </div>
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
