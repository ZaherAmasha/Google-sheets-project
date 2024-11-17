// The onButtonPress function is linked to the 'Fetch Product Recommendations' box in sheet 1 (User Input).
// Similarly, the OnCancelRetrieval function is linked to the 'Cancel Product Retrieval' box.
// The _fetchFromYT is called within a for loop in _fetchYTVidoesForMultipleKeywords to fetch YT videos
// for multiple search keywords. And the latter is called in onButtonPress after the product fetch trigger
// endpoint is called.


function OnButtonPress() {
  var spread_sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("User Input")
  var secret = PropertiesService.getScriptProperties().getProperty("shared_secret");
  Logger.log("Fetching the status of the running tasks from the python server")
  // Checking first if there's a task running. If so, we should not send the trigger to fetch products
  var url = "https://google-sheets-project-1.onrender.com/fetch_status";
  var options = {
      method: "get",
      contentType: "application/json",
      muteHttpExceptions: true,
      headers: {
        "accept": "application/json",
        "Authorization": "Bearer " + secret
      },
      payload: ""
  };
  var response = UrlFetchApp.fetch(url, options);
  Logger.log("This is the response from the status check" + response.getContentText())
  var statusCell = spread_sheet.getRange("C2"); 
  Logger.info("This is the text of the object keys from the fetch status response: "+Object.keys(response))

  // Only triggers the product fetch if there are no tasks running.
  if (response.getContentText().length === 2){
    Logger.info("No job is running, so a new fetch job is triggered")
    statusCell.setValue("Fetching Products, Please Wait")

    // Get the shared_secret for the api auth
    var secret = PropertiesService.getScriptProperties().getProperty("shared_secret");

    // Getting the last row and saving the keyword list
    var lastRow = spread_sheet.getLastRow() + 1;
    var keywordColumn = spread_sheet.getRange("A2:A" + lastRow).getValues().flat();
    Logger.log("These are the keywords: "+keywordColumn)

    // Filter out empty strings and whitespace-only strings
    var filteredKeywords = keywordColumn.filter(function(item) {
      return item.trim() !== "";
    });
    Logger.log("These are the filteredKeywords: " + filteredKeywords);

    // Trigger the fetch webhook
    var url = "https://google-sheets-project-1.onrender.com/trigger_product_fetch";
    var options = {
        method: "post",
        contentType: "application/json",
        muteHttpExceptions: true,
        headers: {
          "accept": "application/json",
          "Authorization": "Bearer " + secret
        },
        payload: JSON.stringify({
            keywords: keywordColumn,
        })
    };
    var response = UrlFetchApp.fetch(url, options);
    Logger.log("This is the response" + response.getContentText())

    _fetchYTVidoesForMultipleKeywords(filteredKeywords)

  }else{
    Logger.info("Get product recommendations button was pressed but there are fetch jobs still running")
    statusCell.setValue("Product Retrieval is already running, please wait")
  }
}

//-----------------------------------------------------------------------------------------------------------------------

// Button to cancel the product retrieval, we send a post request to the python server to stop
function OnCancelRetrieval() {
  // Trigger the fetch webhook
  var url = "https://google-sheets-project-1.onrender.com/cancel_product_fetch";
  var secret = PropertiesService.getScriptProperties().getProperty("shared_secret");
  var options = {
      method: "post",
      contentType: "application/json",
      muteHttpExceptions: true,
      headers: {
        "accept": "application/json",
        "Authorization": "Bearer " + secret
      },
      payload: ""
  };
  var response = UrlFetchApp.fetch(url, options);
  Logger.log("This is the cancel response: " + response.getContentText())
  var spread_sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("User Input")
  var statusCell = spread_sheet.getRange("C2"); 
  statusCell.setValue("Fetching Products cancelled");
}


//-----------------------------------------------------------------------------------------------------------------------

// Function to fetch videos for a single keyword
function _fetchFromYT(keyword) {
  const youTubeResults = YouTube.Search.list('id,snippet', {
    q: keyword,
    type: 'video',
    maxResults: 10
  });

  // Get basic video information
  const videos = youTubeResults.items.map((item) => {
    return {
      video_id: item.id.videoId,
      url: 'https://youtu.be/' + item.id.videoId,
      title: item.snippet.title,
      channel_name: item.snippet.channelTitle,
      description: item.snippet.description,
      published_at: new Date(item.snippet.publishedAt),
      thumbnailUrl: item.snippet.thumbnails.high.url
    };
  });

  // Get video IDs for statistics
  const video_ids = videos.map(video => video.video_id).join(",");
  const sr = YouTube.Videos.list("statistics", {id: video_ids});

  // Merging video details with statistics
  const mergedData = videos.map((video, index) => {
    const stats = sr.items[index].statistics;
    return [
      video.title,
      video.channel_name,
      video.url,
      video.description,
      stats.likeCount,
      stats.viewCount,
      video.published_at,
      video.thumbnailUrl,
    ];
  });
  return mergedData;
}

//-----------------------------------------------------------------------------------------------------------------------

// Main function to handle multiple keywords
function _fetchYTVidoesForMultipleKeywords(keywords) {

  // Get the spreadsheet and sheets
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet3 = ss.getSheetByName('YouTube Videos');

  // Clear existing content except headers
  const lastRow = sheet3.getLastRow();
  if (lastRow > 1) {
    sheet3.deleteRows(2, lastRow - 1);
    sheet3
  }

  // Write headers at the top
  const headers = [
    ['Title', 'Channel Name', 'URL', 'Description', 'Likes', 'Views',
     'Published At', 'Thumbnail URL']
  ];
  // Adding a colored row in between for better visual appeal.
  sheet3.getRange(1, 1, 1, headers[0].length).setValues(headers);
  sheet3.getRange(1, 1, 1, headers[0].length)
    .setBackground('#f3f3f3') // this is white smoke / grey
    .setFontWeight('bold');

  let currentRow = 1;
  
  // Process each keyword
  keywords.forEach((keyword, keywordIndex) => {
    // Add empty row between keyword groups (except for first group)
    if (keywordIndex > 0) {
      currentRow++;
    }

    // Fetch data for single keyword
    const videoData = _fetchFromYT(keyword);
    
    // Create keyword header row
    const keywordHeaderRow = [[`Videos for keyword: ${keyword}`, '', '', '', '', '', '', '']];
  
    // Write keyword header
    sheet3.getRange(currentRow + 1, 1, 1, 8).setValues(keywordHeaderRow);
    sheet3.getRange(currentRow + 1, 1, 1, 8).merge();
    sheet3.getRange(currentRow + 1, 1, 1, 8)
      .setBackground('#e6e6e6') // this is a lighter shade of grey than white smoke
      .setFontWeight('bold')
      .setHorizontalAlignment('center');

    // Write data for this keyword group
    const dataRange = sheet3.getRange(currentRow + 2, 1, videoData.length, 8);
    dataRange.setValues(videoData)
      .setBackground('#ffffff') // this is white
      .setFontWeight('normal')
      .setHorizontalAlignment('left');

    // Format date column
    const dateRange = sheet3.getRange(currentRow + 2, 7, videoData.length, 1);
    dateRange.setNumberFormat('yyyy-mm-dd hh:mm:ss');
    
    // Format numbers columns (likes and views)
    const numberRanges = sheet3.getRange(currentRow + 2, 5, videoData.length, 2);
    numberRanges.setNumberFormat('#,##0');
    
    // Update current row position
    currentRow += videoData.length + 1;
  });

  // Auto-resize all columns
  sheet3.autoResizeColumns(1, 8);
}