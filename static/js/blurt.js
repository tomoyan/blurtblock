$(document).ready(function(){
    $("#nav-follower-tab").click(function(){
        $.ajax(document.follower_api,
        {
            dataType: 'json', // type of response data
            timeout: 60000,     // timeout milliseconds
            success: function (data, status, xhr) {   // success callback function
                var size = Object.keys(data).length;
                if (size === undefined) {
                    size = 0;
                }
                $("#followerSize").html(size);

                // liStr holds html list
                var liStr = ``;
                if (jQuery.isEmptyObject(data)) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Follower Data</span></li>`;
                    $("#followerResult").html(liStr);
                }
                else {
                   $("#followerResult").empty();
                   $.each(data, function(key, data){
                        if (data) {
                        liStr = `
                            <li class="list-group-item" data-field=>
                                <span><img src="https://images.blurt.blog/u/${key}/avatar/small"
                                        onerror="this.onerror=null;
                                        this.src='/static/images/blurt_profile.png';"
                                        alt="profile_image"
                                        class="img-thumbnail rounded-circle float-left mr-3"
                                        width="auto"></span>
                                <span>
                                    <a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${key}"
                                        target="_blank" rel="noopener noreferrer">${key}
                                    </a></span>
                                <span class="badge badge-blurt font-weight-light">Following</span>
                                <br>
                                <span>
                                    <a class="text-blurt mr-3" href="https://blurtblock.herokuapp.com/${key}"
                                        target="_blank" rel="noopener noreferrer">Profile
                                    </a></span>
                            </li>`;
                        }
                        else {
                        liStr = `
                            <li class="list-group-item" data-field=>
                                <span><img src="https://images.blurt.blog/u/${key}/avatar/small"
                                        onerror="this.onerror=null;
                                        this.src='/static/images/blurt_profile.png';"
                                        alt="profile_image"
                                        class="img-thumbnail rounded-circle float-left mr-3"
                                        width="auto"></span>
                                <span>
                                    <a class="text-blurt font-weight-bold" href="https://blurt.blog/@${key}"
                                    target="_blank" rel="noopener noreferrer">${key}
                                    </a></span>
                                <br>
                                <span>
                                    <a class="text-blurt mr-3" href="https://blurtblock.herokuapp.com/${key}"
                                        target="_blank" rel="noopener noreferrer">Profile
                                    </a></span>
                            </li>`;
                        }

                        $("#followerResult").append(liStr);
                    });
               }
            },
            // error: function (jqXhr, textStatus, errorMessage) { // error callback
            //     $("#followerResult").append('Error: ' + errorMessage);
            // }
        });
    });

    $("#nav-following-tab").click(function(){
        $.ajax(document.following_api,
        {
            dataType: 'json', // type of response data
            timeout: 60000,     // timeout milliseconds
            success: function (data, status, xhr) {   // success callback function
                var size = Object.keys(data).length;
                if (size === undefined) {
                    size = 0;
                }
                $("#followingSize").html(size);

                // liStr holds html list
                var liStr = ``;
                if (jQuery.isEmptyObject(data)) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Following Data</span></li>`;
                    $("#followingResult").html(liStr);
                }
                else {
                   $("#followingResult").empty();
                   $.each(data, function(key, data){
                        if (data) {
                        liStr = `
                            <li class="list-group-item" data-field=>
                                <span><img src="https://images.blurt.blog/u/${key}/avatar/small"
                                        onerror="this.onerror=null;
                                        this.src='/static/images/blurt_profile.png';"
                                        alt="profile_image"
                                        class="img-thumbnail rounded-circle float-left mr-3"
                                        width="auto"></span>
                                <span>
                                    <a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${key}"
                                        target="_blank" rel="noopener noreferrer">${key}
                                    </a></span>
                                <span class="badge badge-blurt font-weight-light">Follows you</span>
                                <br>
                                <span>
                                    <a class="text-blurt mr-3" href="https://blurtblock.herokuapp.com/${key}"
                                        target="_blank" rel="noopener noreferrer">Profile
                                    </a></span>
                            </li>`;
                        }
                        else {
                        liStr = `
                            <li class="list-group-item" data-field=>
                                <span><img src="https://images.blurt.blog/u/${key}/avatar/small"
                                        onerror="this.onerror=null;
                                        this.src='/static/images/blurt_profile.png';"
                                        alt="profile_image"
                                        class="img-thumbnail rounded-circle float-left mr-3"
                                        width="auto"></span>
                                <span>
                                    <a class="text-blurt font-weight-bold" href="https://blurt.blog/@${key}"
                                        target="_blank" rel="noopener noreferrer">${key}
                                    </a></span>
                                <br>
                                <span>
                                    <a class="text-blurt mr-3" href="https://blurtblock.herokuapp.com/${key}"
                                        target="_blank" rel="noopener noreferrer">Profile
                                    </a></span>
                            </li>`;
                        }

                        $("#followingResult").append(liStr);
                    });
               }
            },
            // error: function (jqXhr, textStatus, errorMessage) { // error callback
            //     $("#followingResult").append('Error: ' + errorMessage);
            // }
        });
    });

    $("#nav-mute-tab").click(function(){
        $.ajax(document.mute_api,
        {
            dataType: 'json', // type of response data
            timeout: 60000,     // timeout milliseconds
            success: function (data, status, xhr) {   // success callback function
                var size = Object.keys(data['muting']).length + Object.keys(data['muter']).length;
                if (size === undefined) {
                    size = 0;
                }
                $("#muteSize").html(size);
                // console.log(data['muter']);

                // liStr holds html list
                var liStr = ``;
                if (jQuery.isEmptyObject(data['muting'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>Not Muting Anybody</span></li>`;
                    $("#mutingResult").html(liStr);
                }
                else {
                   $("#mutingResult").empty();
                   $.each(data['muting'], function(index, value){
                        liStr = `
                            <li class="list-group-item" data-field=>
                                <span><img src="https://images.blurt.blog/u/${value}/avatar/small"
                                        onerror="this.onerror=null;
                                        this.src='/static/images/blurt_profile.png';"
                                        alt="profile_image"
                                        class="img-thumbnail rounded-circle float-left mr-3"
                                        width="auto"></span>
                                <span>
                                    <a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${value}"
                                        target="_blank" rel="noopener noreferrer">${value}
                                    </a></span>
                                <br>
                                <span>
                                    <a class="text-blurt mr-3" href="https://blurtblock.herokuapp.com/${value}"
                                        target="_blank" rel="noopener noreferrer">Profile
                                    </a></span>
                            </li>`;

                        $("#mutingResult").append(liStr);
                    });
               }

                if (jQuery.isEmptyObject(data['muter'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>Not Muted by Anybody</span></li>`;
                    $("#muteResult").html(liStr);
                }
                else {
                   $("#muteResult").empty();
                   $.each(data['muter'], function(index, value){
                        liStr = `
                            <li class="list-group-item" data-field=>
                                <span><img src="https://images.blurt.blog/u/${value}/avatar/small"
                                        onerror="this.onerror=null;
                                        this.src='/static/images/blurt_profile.png';"
                                        alt="profile_image"
                                        class="img-thumbnail rounded-circle float-left mr-3"
                                        width="auto"></span>
                                <span>
                                    <a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${value}"
                                        target="_blank" rel="noopener noreferrer">${value}
                                    </a></span>
                                <br>
                                <span>
                                    <a class="text-blurt mr-3" href="https://blurtblock.herokuapp.com/${value}"
                                        target="_blank" rel="noopener noreferrer">Profile
                                    </a></span>
                            </li>`;

                        $("#muteResult").append(liStr);
                    });
               }

            },
            // error: function (jqXhr, textStatus, errorMessage) { // error callback
            //     $("#muteResult").append('Error: ' + errorMessage);
            // }
        });
    });

    $("#nav-delegation-tab").click(function(){
        // incoming elegation
        $.ajax(document.delegationApiIn,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            tryCount : 0,
            retryLimit : 6, // retry times
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
                                    <span><img src="https://images.blurt.blog/u/${value.delegator}/avatar/small"
                                            onerror="this.onerror=null;
                                            this.src='/static/images/blurt_profile.png';"
                                            alt="profile_image"
                                            class="img-thumbnail rounded-circle float-left mr-3"
                                            width="auto">
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
            error: function (jqXhr, textStatus, errorMessage) { // error callback
                if (textStatus == 'timeout') {
                    this.tryCount++;
                    if (this.tryCount < this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    }
                }
                $("#incomingResult").html('Oops! ' + errorMessage + ' Please reload');
            }
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
                                    <span><img src="https://images.blurt.blog/u/${value.delegatee}/avatar/small"
                                            onerror="this.onerror=null;
                                            this.src='/static/images/blurt_profile.png';"
                                            alt="profile_image"
                                            class="img-thumbnail rounded-circle float-left mr-3"
                                            width="auto">
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

    $("#rewards-tab").click(function(){
        // 1 day rewards summary
        $.ajax(document.rewardOne_api,
        {
            dataType: 'json', // type of response data
            timeout: 60000, // timeout milliseconds
            success: function (data, status, xhr) {
                var authorBP = ``;
                var curationBP = ``;
                var producerBP = ``;
                var totalBP = ``;

                if (jQuery.isEmptyObject(data)) {
                    authorBP = `0 BP`;
                    curationBP = `0 BP`;
                    producerBP = `0 BP`;
                    totalBP = `0 BP`;
                }
                else {
                    authorBP = `${data['author']} BP`;
                    curationBP = `${data['curation']} BP`;
                    producerBP = `${data['producer']} BP`;
                    totalBP = `${data['total']} BP`;
                }

                $("#authorOne").html(authorBP);
                $("#curationOne").html(curationBP);
                $("#producerOne").html(producerBP);
                $("#totalOne").html(totalBP);
            },
            error: function (jqXhr, textStatus, errorMessage) { // error callback
                $("#authorOne").remove();
                $("#curationOne").remove();
                $("#producerOne").remove();
                $("#totalOne").remove();
            }
        });

        // 7 day rewards summary
        $.ajax(document.rewardSeven_api,
        {
            dataType: 'json', // type of response data
            timeout: 60000, // timeout milliseconds
            success: function (data, status, xhr) {
                var authorBP = ``;
                var curationBP = ``;
                var producerBP = ``;
                var totalBP = ``;

                if (jQuery.isEmptyObject(data)) {
                    authorBP = `0 BP`;
                    curationBP = `0 BP`;
                    producerBP = `0 BP`;
                    totalBP = `0 BP`;
                }
                else {
                    authorBP = `${data['author']} BP`;
                    curationBP = `${data['curation']} BP`;
                    producerBP = `${data['producer']} BP`;
                    totalBP = `${data['total']} BP`;
                }

                $("#authorSeven").html(authorBP);
                $("#curationSeven").html(curationBP);
                $("#producerSeven").html(producerBP);
                $("#totalSeven").html(totalBP);
            },
            error: function (jqXhr, textStatus, errorMessage) { // error callback
                $("#authorSeven").remove();
                $("#curationSeven").remove();
                $("#producerSeven").remove();
                $("#totalSeven").remove();
            }
        });

        // var total30 = `0.000`;
        // 30 day rewards summary
        $.ajax(document.rewardThirtyApi,
        {
            dataType: 'json', // type of response data
            timeout: 30000, // 30 sec timeout in milliseconds
            tryCount : 0,
            retryLimit : 3, // rety 3 times
            success: function (data, status, xhr) {
                var authorBP = `0.000 BP`;
                var curationBP = `0.000 BP`;
                var producerBP = `0.000 BP`;
                var totalBP = `0.000 BP`;

                if (jQuery.isEmptyObject(data)) {
                    authorBP = `0.000 BP`;
                    curationBP = `0.000 BP`;
                    producerBP = `0.000 BP`;
                    totalBP = `0.000 BP`;
                }
                else {
                    authorBP = `${data['author']} BP`;
                    curationBP = `${data['curation']} BP`;
                    producerBP = `${data['producer']} BP`;
                    totalBP = `${data['total']} BP`;
                }

                $("#loadingImage").remove();
                $("#authorThirty").html(authorBP);
                $("#curationThirty").html(curationBP);
                $("#producerThirty").html(producerBP);
                $("#totalThirty").html(totalBP);
            },
            error: function (jqXhr, textStatus, errorMessage) {
                if (textStatus == 'timeout') {
                    this.tryCount++;
                    if (this.tryCount < this.retryLimit) {
                        //try again
                        $.ajax(this);
                        return;
                    }
                    // return;
                }
                // else {
                $("#loadingImage").remove();
                $("#authorThirty").html(`0.000 BP`);
                $("#curationThirty").html(`0.000 BP`);
                $("#producerThirty").html(`0.000 BP`);
                $("#totalThirty").html(`0.000 BP`);
                // }
            }
        });

    });

    $("#transferHistory").click(function(){
        // transfer history
        $.ajax(document.transferHistoryApi,
        {
            dataType: 'json', // type of response data
            timeout: 60000, // 30 sec timeout in milliseconds
            success: function (data, status, xhr) {
                let transactions = ``
                let BASE = 'https://blurtblock.herokuapp.com'

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
                                        ${value['amount']} BLURT
                                        <a class="text-blurt"
                                            href="${BASE}/${value['from']}"
                                            target="_blank" rel="noopener noreferrer">${value['from']}
                                        </a>
                                        to
                                        <a class="text-blurt"
                                            href="${BASE}/${value['to']}"
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
            timeout: 60000, // 60 sec timeout in milliseconds
            success: function (data, status, xhr) {
                let transactions = ``
                let BASE = 'https://blurtblock.herokuapp.com'
                let BLURT = 'https://blurt.world'

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
                                            href="${BASE}/${value['voter']}"
                                            target="_blank" rel="noopener noreferrer">${value['voter']}
                                        </a>
                                        voted
                                        <a class="text-blurt"
                                            href="${BASE}/${value['author']}"
                                            target="_blank" rel="noopener noreferrer">${value['author']}
                                        </a>
                                        (${value['weight']}%)
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate"
                                        style="max-width: 500px;">
                                        <a class="text-blurt"
                                            href="${BLURT}/@${value['author']}/${value['permlink']}"
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
            timeout: 60000, // 60 sec timeout in milliseconds
            success: function (data, status, xhr) {
                let transactions = ``
                let BASE = 'https://blurtblock.herokuapp.com'
                let BLURT = 'https://blurt.world'

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
                                            href="${BASE}/${value['author']}"
                                            target="_blank" rel="noopener noreferrer">${value['author']}
                                        </a>
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate">
                                        ${value['body']}
                                    </div>
                                    <div class="col-sm-auto text-sm-left text-truncate"
                                        style="max-width: 500px;">
                                        <a class="text-blurt"
                                            href="${BLURT}/@${value['author']}/${value['permlink']}"
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
});
