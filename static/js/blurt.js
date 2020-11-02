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
                // console.log(Object.keys(data).length);

                // liStr holds html list
                var liStr = ``;
                if (jQuery.isEmptyObject(data)) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Follower Data</span></li>`;
                    $("#followerResult").html(liStr);
                }
                else {
                   $("#followerResult").html(" ");
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
                // console.log(Object.keys(data).length);

                // liStr holds html list
                var liStr = ``;
                if (jQuery.isEmptyObject(data)) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Following Data</span></li>`;
                    $("#followingResult").html(liStr);
                }
                else {
                   $("#followingResult").html(" ");
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
                // console.log(data['muting']);
                // console.log(Object.keys(data).length);

                // liStr holds html list
                var liStr = ``;
                if (jQuery.isEmptyObject(data['muting'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>Not Muting Anybody</span></li>`;
                    $("#mutingResult").html(liStr);
                }
                else {
                   $("#mutingResult").html(" ");
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
                   $("#muteResult").html(" ");
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
        $.ajax(document.delegation_api,
        {
            dataType: 'json', // type of response data
            timeout: 60000,     // timeout milliseconds
            success: function (data, status, xhr) {   // success callback function
                var size = Object.keys(data['incoming']).length
                    + Object.keys(data['outgoing']).length
                    + Object.keys(data['expiring']).length;
                if (size === undefined) {
                    size = 0;
                }
                $("#delegationSize").html(size);

                // liStr holds html list
                var liStr = ``;
                if (jQuery.isEmptyObject(data['incoming'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Incoming Delegation (not implemented)</span></li>`;
                    $("#incomingResult").html(liStr);
                }
                else {
                   $("#incomingResult").html(" ");
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
                                        <a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${value.delegator}"
                                            target="_blank" rel="noopener noreferrer">
                                            ${value.delegator}</a>
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

                if (jQuery.isEmptyObject(data['outgoing'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Outgoing Delegation</span></li>`;
                    $("#outgoingResult").html(liStr);
                }
                else {
                   $("#outgoingResult").html(" ");
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
                                        <a class="text-blurt font-weight-bold mr-3" href="https://blurt.blog/@${value.delegatee}"
                                            target="_blank" rel="noopener noreferrer">
                                            ${value.delegatee}</a>
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

                if (jQuery.isEmptyObject(data['expiring'])) {
                    liStr = `
                    <li class="list-group-item" data-field=><span>No Expiring Delegation</span></li>`;
                    $("#expiringResult").html(liStr);
                }
                else {
                   $("#expiringResult").html(" ");
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
            // error: function (jqXhr, textStatus, errorMessage) { // error callback
            //     $("#incomingResult").append('Error: ' + errorMessage);
            // }
        });
    });

    $("#nav-reward-tab").click(function(){
        $.ajax(document.reward_api,
        {
            dataType: 'json', // type of response data
            timeout: 60000,     // timeout milliseconds
            success: function (data, status, xhr) {   // success callback function
                var size = Object.keys(data).length;
                if (size === undefined) {
                    size = 0;
                }
                $("#rewardSize").html(" ");
                // console.log(Object.keys(data).length);

                // liStr holds html list
                var liStr = ``;
                if (jQuery.isEmptyObject(data)) {
                    liStr = `
                    <li class="list-group-item" data-field=>
                        <span>No Rewards Data</span>
                    </li>`;
                }
                else {
                    liStr = `
                        <li class="list-group-item" data-field=>
                            <div class="container">
                              <div class="row">
                                <div class="col-sm text-left">
                                    <span class="font-weight-bold">
                                        Duration
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span class="font-weight-bold">
                                        Author BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span class="font-weight-bold">
                                        Curation BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span class="font-weight-bold">
                                        Producer BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span class="font-weight-bold">
                                        Total BP
                                    </span>
                                </div>
                              </div>
                            </div>
                        </li>
                        <li class="list-group-item" data-field=>
                            <div class="container">
                              <div class="row">
                                <div class="col-sm text-left">
                                    <span>
                                        Last 24 Hours
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span>
                                        ${data['author_day']} BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span>
                                        ${data['curation_day']} BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span>
                                        ${data['producer_day']} BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span>
                                        ${data['total_day']} BP
                                    </span>
                                </div>
                              </div>
                            </div>
                        </li>
                        <li class="list-group-item" data-field=>
                            <div class="container">
                              <div class="row">
                                <div class="col-sm text-left">
                                    <span>
                                        Last 7 Days
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span>
                                        ${data['author_week']} BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span>
                                        ${data['curation_week']} BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span>
                                        ${data['producer_week']} BP
                                    </span>
                                </div>
                                <div class="col-sm text-right">
                                    <span>
                                        ${data['total_week']} BP
                                    </span>
                                </div>
                              </div>
                            </div>
                        </li>`;
                    $("#rewardResult").html(liStr);
               }
            },
        });
    });

});
