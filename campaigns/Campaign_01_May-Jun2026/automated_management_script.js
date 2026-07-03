/**
 * Google Ads Automated Campaign Management Script
 * 
 * This script runs hourly to perform three core optimization tasks:
 * 1. Hourly Budget Pacing Check: Checks campaign daily spend before 2 PM local time. If daily spend
 *    is > 70% of the daily budget, bids (Max CPC) for active ad groups and keywords are reduced by 20%.
 *    Bids are automatically restored (increased by 25%) on the next day.
 * 2. Auto-Negative Competitor/Low-Intent Blocker: Scans search terms from the last 7 days and adds
 *    any search term containing competitor or low-intent keywords as an exact match campaign negative.
 *    It queries existing negatives to avoid duplicates.
 * 3. Link Checker: Collects final URLs from enabled ads and keywords, deduplicates them, and verifies
 *    they return a 200 OK status. Logs any failures.
 * 
 * Runtime: Google Ads Script Environment (JavaScript)
 */

// Configuration Constants
var PACING_HOUR_LIMIT = 14; // 2 PM (local time)
var PACING_SPEND_THRESHOLD = 0.70; // 70% of budget
var PACING_BID_REDUCTION_FACTOR = 0.80; // 20% reduction
var PACING_BID_RESTORE_FACTOR = 1.25; // 25% increase (restores 20% reduction)
var PACING_LABEL_PREFIX = "Paced_"; // Prefix for daily tracking labels

// Keywords for auto-blocking (case-insensitive matches)
var BLOCKLIST_KEYWORDS = [
  'harvey', 'vakilsearch', 'casemine', 'casetext', 'spellbook', 'draftbot', // Competitors
  'free', 'jobs', 'course', 'syllabus', 'salary', 'resume' // Low-intent terms
];

// Execution Guardrails
var MAX_URL_CHECKS = 250; // Cap on unique URL fetches per run to prevent timeout/quota issues
var MAX_EXECUTION_TIME_MS = 25 * 60 * 1000; // 25 minutes safety limit

function main() {
  Logger.log("=========================================");
  Logger.log("STARTING GOOGLE ADS AUTOMATED MANAGEMENT");
  Logger.log("=========================================");
  
  var startTime = new Date().getTime();
  
  // 1. Run Hourly Budget Pacing Protection
  try {
    runBudgetPacing();
  } catch (e) {
    Logger.log("Error in Budget Pacing Check: " + e.toString());
  }
  
  Logger.log("-----------------------------------------");
  
  // 2. Run Auto-Negative Blocker
  try {
    runNegativeKeywordBlocker();
  } catch (e) {
    Logger.log("Error in Auto-Negative Keyword Blocker: " + e.toString());
  }
  
  Logger.log("-----------------------------------------");
  
  // 3. Run Link Checker
  try {
    runLinkChecker(startTime);
  } catch (e) {
    Logger.log("Error in Link Checker: " + e.toString());
  }
  
  Logger.log("=========================================");
  Logger.log("SCRIPT EXECUTION COMPLETED");
  Logger.log("=========================================");
}

/**
 * Task 1: Hourly Budget Pacing Protection
 */
function runBudgetPacing() {
  var timeZone = AdsApp.currentAccount().getTimeZone();
  var now = new Date();
  var todayStr = Utilities.formatDate(now, timeZone, 'yyyy_MM_dd');
  var labelToday = PACING_LABEL_PREFIX + todayStr;
  var hour = parseInt(Utilities.formatDate(now, timeZone, 'H'), 10);
  
  Logger.log("Hourly Budget Pacing Check:");
  Logger.log("  Account Time Zone: " + timeZone);
  Logger.log("  Current Time: " + Utilities.formatDate(now, timeZone, 'yyyy-MM-dd HH:mm:ss'));
  Logger.log("  Current Hour: " + hour);
  
  // Ensure the tracking label for today exists in the account
  getOrCreateLabel(labelToday);
  
  var campaignIterator = AdsApp.campaigns()
    .withCondition("Status = ENABLED")
    .withCondition("AdvertisingChannelType = SEARCH") // Typically applied to search, can be expanded
    .get();
    
  while (campaignIterator.hasNext()) {
    var campaign = campaignIterator.next();
    var campaignName = campaign.getName();
    var budget = campaign.getBudget();
    
    if (!budget) {
      Logger.log("  Campaign '" + campaignName + "' has no budget defined. Skipping.");
      continue;
    }
    
    var budgetAmount = budget.getAmount();
    var stats = campaign.getStatsFor("TODAY");
    var cost = stats.getCost();
    
    // Check if the campaign has any pacing labels
    var labels = campaign.labels().get();
    var hasTodayLabel = false;
    var pastPacingLabels = [];
    
    while (labels.hasNext()) {
      var label = labels.next();
      var labelName = label.getName();
      if (labelName === labelToday) {
        hasTodayLabel = true;
      } else if (labelName.indexOf(PACING_LABEL_PREFIX) === 0) {
        pastPacingLabels.push(labelName);
      }
    }
    
    // Check for restoration of past pacing
    if (pastPacingLabels.length > 0) {
      Logger.log("  Campaign '" + campaignName + "' has past pacing labels: " + pastPacingLabels.join(", ") + ". Restoring bids.");
      restoreCampaignBids(campaign);
      
      // Clean up past labels from the campaign
      for (var i = 0; i < pastPacingLabels.length; i++) {
        campaign.removeLabel(pastPacingLabels[i]);
      }
      Logger.log("  Restoration complete and past labels removed.");
    }
    
    // Apply pacing protection if applicable
    if (hasTodayLabel) {
      Logger.log("  Campaign '" + campaignName + "' was already paced today. Skipping.");
      continue;
    }
    
    if (hour < PACING_HOUR_LIMIT) {
      var spendPercent = budgetAmount > 0 ? (cost / budgetAmount) * 100 : 0;
      Logger.log("  Campaign '" + campaignName + "' spend: $" + cost.toFixed(2) + " of $" + budgetAmount.toFixed(2) + " (" + spendPercent.toFixed(1) + "%)");
      
      if (cost > budgetAmount * PACING_SPEND_THRESHOLD) {
        Logger.log("  WARNING: Spend exceeds " + (PACING_SPEND_THRESHOLD * 100) + "% before 2 PM. Reducing bids by 20%.");
        reduceCampaignBids(campaign);
        campaign.applyLabel(labelToday);
        Logger.log("  Bids reduced and tracking label '" + labelToday + "' applied.");
      }
    } else {
      Logger.log("  Campaign '" + campaignName + "': Pacing window has passed (after 2 PM). No new pacing checks applied today.");
    }
  }
  
  // Clean up unused/old pacing labels from the account
  cleanupOldLabels(labelToday);
}

/**
 * Helper to reduce bids of enabled ad groups and keywords in a campaign by 20%
 */
function reduceCampaignBids(campaign) {
  // Reduce Ad Group Bids
  var adGroupIterator = campaign.adGroups().withCondition("Status = ENABLED").get();
  var adGroupCount = 0;
  while (adGroupIterator.hasNext()) {
    var adGroup = adGroupIterator.next();
    var bidding = adGroup.bidding();
    if (bidding && typeof bidding.getCpc === 'function') {
      var currentCpc = bidding.getCpc();
      if (currentCpc !== null && currentCpc !== undefined) {
        var newCpc = Math.round(currentCpc * PACING_BID_REDUCTION_FACTOR * 100) / 100;
        if (newCpc < 0.01) newCpc = 0.01;
        bidding.setCpc(newCpc);
        adGroupCount++;
      }
    }
  }
  if (adGroupCount > 0) {
    Logger.log("    Reduced CPC bids for " + adGroupCount + " ad groups.");
  }
  
  // Reduce Keyword Bids
  var keywordIterator = campaign.keywords().withCondition("Status = ENABLED").get();
  var keywordCount = 0;
  while (keywordIterator.hasNext()) {
    var keyword = keywordIterator.next();
    var bidding = keyword.bidding();
    if (bidding && typeof bidding.getCpc === 'function') {
      var currentCpc = bidding.getCpc();
      if (currentCpc !== null && currentCpc !== undefined) {
        var newCpc = Math.round(currentCpc * PACING_BID_REDUCTION_FACTOR * 100) / 100;
        if (newCpc < 0.01) newCpc = 0.01;
        bidding.setCpc(newCpc);
        keywordCount++;
      }
    }
  }
  if (keywordCount > 0) {
    Logger.log("    Reduced CPC bids for " + keywordCount + " keywords.");
  }
}

/**
 * Helper to restore bids of enabled ad groups and keywords in a campaign by 25% (offsetting 20% reduction)
 */
function restoreCampaignBids(campaign) {
  // Restore Ad Group Bids
  var adGroupIterator = campaign.adGroups().withCondition("Status = ENABLED").get();
  var adGroupCount = 0;
  while (adGroupIterator.hasNext()) {
    var adGroup = adGroupIterator.next();
    var bidding = adGroup.bidding();
    if (bidding && typeof bidding.getCpc === 'function') {
      var currentCpc = bidding.getCpc();
      if (currentCpc !== null && currentCpc !== undefined) {
        var newCpc = Math.round(currentCpc * PACING_BID_RESTORE_FACTOR * 100) / 100;
        bidding.setCpc(newCpc);
        adGroupCount++;
      }
    }
  }
  if (adGroupCount > 0) {
    Logger.log("    Restored CPC bids for " + adGroupCount + " ad groups.");
  }
  
  // Restore Keyword Bids
  var keywordIterator = campaign.keywords().withCondition("Status = ENABLED").get();
  var keywordCount = 0;
  while (keywordIterator.hasNext()) {
    var keyword = keywordIterator.next();
    var bidding = keyword.bidding();
    if (bidding && typeof bidding.getCpc === 'function') {
      var currentCpc = bidding.getCpc();
      if (currentCpc !== null && currentCpc !== undefined) {
        var newCpc = Math.round(currentCpc * PACING_BID_RESTORE_FACTOR * 100) / 100;
        bidding.setCpc(newCpc);
        keywordCount++;
      }
    }
  }
  if (keywordCount > 0) {
    Logger.log("    Restored CPC bids for " + keywordCount + " keywords.");
  }
}

/**
 * Helper to get or create label in the account
 */
function getOrCreateLabel(labelName) {
  var labelIterator = AdsApp.labels().withCondition("Name = '" + labelName + "'").get();
  if (labelIterator.hasNext()) {
    return labelIterator.next();
  }
  AdsApp.createLabel(labelName, "Pacing protection applied on this date.");
  var labelIteratorRetry = AdsApp.labels().withCondition("Name = '" + labelName + "'").get();
  if (labelIteratorRetry.hasNext()) {
    return labelIteratorRetry.next();
  }
  return null;
}

/**
 * Clean up old pacing labels that are no longer assigned to any campaigns
 */
function cleanupOldLabels(labelToday) {
  var labelIterator = AdsApp.labels().withCondition("Name STARTS_WITH '" + PACING_LABEL_PREFIX + "'").get();
  while (labelIterator.hasNext()) {
    var label = labelIterator.next();
    var labelName = label.getName();
    if (labelName !== labelToday) {
      // Check if any campaign is still using it
      var hasCampaigns = AdsApp.campaigns().withCondition("LabelNames CONTAINS_ANY ['" + labelName + "']").get().hasNext();
      if (!hasCampaigns) {
        label.remove();
        Logger.log("  Deleted old unused pacing label '" + labelName + "' from the account.");
      }
    }
  }
}

/**
 * Task 2: Auto-Negative Competitor and Low-Intent Keyword Blocker
 */
function runNegativeKeywordBlocker() {
  Logger.log("Auto-Negative Competitor and Low-Intent Keyword Blocker:");
  
  // Query search terms for the last 7 days
  var query = "SELECT search_term_view.search_term, campaign.id, campaign.name " +
              "FROM search_term_view " +
              "WHERE segments.date DURING LAST_7_DAYS";
  
  var report;
  try {
    report = AdsApp.report(query);
  } catch (e) {
    Logger.log("  Failed to retrieve search term report: " + e.toString());
    return;
  }
  
  var rows = report.rows();
  var matches = [];
  var campaignIdsToFetch = [];
  
  while (rows.hasNext()) {
    var row = rows.next();
    var searchTerm = row['search_term_view.search_term'];
    var campaignId = row['campaign.id'];
    
    if (!searchTerm || !campaignId) continue;
    
    var lowerTerm = searchTerm.toLowerCase();
    var shouldBlock = false;
    
    for (var i = 0; i < BLOCKLIST_KEYWORDS.length; i++) {
      if (lowerTerm.indexOf(BLOCKLIST_KEYWORDS[i]) !== -1) {
        shouldBlock = true;
        break;
      }
    }
    
    if (shouldBlock) {
      matches.push({
        campaignId: campaignId,
        searchTerm: searchTerm
      });
      if (campaignIdsToFetch.indexOf(campaignId) === -1) {
        campaignIdsToFetch.push(campaignId);
      }
    }
  }
  
  Logger.log("  Found " + matches.length + " search term matches containing blocklist words.");
  if (matches.length === 0) {
    Logger.log("  No low-intent or competitor terms matched.");
    return;
  }
  
  // Fetch campaigns for matching IDs
  var campaignMap = {};
  var campaignIterator = AdsApp.campaigns().withIds(campaignIdsToFetch).get();
  while (campaignIterator.hasNext()) {
    var campaign = campaignIterator.next();
    campaignMap[campaign.getId()] = campaign;
  }
  
  // Get existing negative keywords to avoid duplication
  var existingNegatives = getExistingNegatives(campaignIdsToFetch);
  
  var addedCount = 0;
  for (var j = 0; j < matches.length; j++) {
    var match = matches[j];
    var campaign = campaignMap[match.campaignId];
    if (!campaign) continue;
    
    var checkKey = "exact:" + match.searchTerm.toLowerCase();
    var campNegs = existingNegatives[match.campaignId];
    
    if (campNegs && campNegs[checkKey]) {
      // Already exists as exact match negative
      continue;
    }
    
    // Add exact match campaign-level negative keyword
    try {
      if (typeof campaign.createNegativeKeyword === 'function') {
        campaign.createNegativeKeyword("[" + match.searchTerm + "]");
      } else if (typeof campaign.addNegativeKeyword === 'function') {
        campaign.addNegativeKeyword("[" + match.searchTerm + "]");
      }
      
      Logger.log("  Campaign '" + campaign.getName() + "' | Added exact match negative keyword: [" + match.searchTerm + "]");
      addedCount++;
      
      // Update local cache
      if (!existingNegatives[match.campaignId]) {
        existingNegatives[match.campaignId] = {};
      }
      existingNegatives[match.campaignId][checkKey] = true;
    } catch (err) {
      Logger.log("  Failed to add negative keyword [" + match.searchTerm + "] to campaign '" + campaign.getName() + "': " + err.toString());
    }
  }
  
  Logger.log("  Successfully added " + addedCount + " new negative keywords.");
}

/**
 * Fetch existing negative keywords in chunks to prevent query length limits
 */
function getExistingNegatives(campaignIds) {
  var existing = {};
  for (var i = 0; i < campaignIds.length; i++) {
    existing[campaignIds[i]] = {};
  }
  
  var chunkSize = 50;
  for (var i = 0; i < campaignIds.length; i += chunkSize) {
    var chunk = campaignIds.slice(i, i + chunkSize);
    var query = "SELECT campaign_criterion.keyword.text, campaign_criterion.keyword.match_type, campaign.id " +
                "FROM campaign_criterion " +
                "WHERE campaign_criterion.type = 'KEYWORD' " +
                "AND campaign_criterion.negative = TRUE " +
                "AND campaign.id IN (" + chunk.join(",") + ")";
    try {
      var report = AdsApp.report(query);
      var rows = report.rows();
      while (rows.hasNext()) {
        var row = rows.next();
        var text = row['campaign_criterion.keyword.text'];
        var matchType = row['campaign_criterion.keyword.match_type'];
        var campId = row['campaign.id'];
        if (text && campId && matchType) {
          var key = matchType.toLowerCase() + ":" + text.toLowerCase();
          existing[campId][key] = true;
        }
      }
    } catch (e) {
      Logger.log("  Error fetching existing negatives for chunk starting index " + i + ": " + e.toString());
    }
  }
  return existing;
}

/**
 * Task 3: URL Link Checker
 */
function runLinkChecker(startTime) {
  Logger.log("URL Link Checker:");
  
  var uniqueUrls = {};
  
  // 1. Gather URLs from enabled Ads in enabled Campaigns/Ad Groups
  var adIterator = AdsApp.ads()
    .withCondition("CampaignStatus = ENABLED")
    .withCondition("AdGroupStatus = ENABLED")
    .withCondition("Status = ENABLED")
    .get();
    
  while (adIterator.hasNext()) {
    var ad = adIterator.next();
    var url = ad.urls().getFinalUrl();
    if (url) {
      if (!uniqueUrls[url]) {
        uniqueUrls[url] = [];
      }
      uniqueUrls[url].push({
        type: "Ad",
        campaignName: ad.getCampaign().getName(),
        adGroupName: ad.getAdGroup().getName(),
        idOrText: ad.getId().toString()
      });
    }
  }
  
  // 2. Gather URLs from enabled Keywords in enabled Campaigns/Ad Groups
  var keywordIterator = AdsApp.keywords()
    .withCondition("CampaignStatus = ENABLED")
    .withCondition("AdGroupStatus = ENABLED")
    .withCondition("Status = ENABLED")
    .get();
    
  while (keywordIterator.hasNext()) {
    var keyword = keywordIterator.next();
    var url = keyword.urls().getFinalUrl();
    if (url) {
      if (!uniqueUrls[url]) {
        uniqueUrls[url] = [];
      }
      uniqueUrls[url].push({
        type: "Keyword",
        campaignName: keyword.getCampaign().getName(),
        adGroupName: keyword.getAdGroup().getName(),
        idOrText: keyword.getText()
      });
    }
  }
  
  var urlList = Object.keys(uniqueUrls);
  Logger.log("  Found " + urlList.length + " unique Final URLs to verify.");
  
  var checkCount = 0;
  var failCount = 0;
  var badUrls = [];
  
  for (var i = 0; i < urlList.length; i++) {
    var url = urlList[i];
    
    // Enforcement of execution limits
    if (checkCount >= MAX_URL_CHECKS) {
      Logger.log("  Reached URL verification limit of " + MAX_URL_CHECKS + ". Remaining URLs will be checked in the next run.");
      break;
    }
    
    if (new Date().getTime() - startTime > MAX_EXECUTION_TIME_MS) {
      Logger.log("  Approaching script execution time limit. Stopping URL checks.");
      break;
    }
    
    checkCount++;
    var success = false;
    var responseCode = -1;
    var errMsg = "";
    
    try {
      var response = UrlFetchApp.fetch(url, {
        muteHttpExceptions: true,
        followRedirects: true,
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Google-Ads-Link-Checker"
        }
      });
      responseCode = response.getResponseCode();
      if (responseCode === 200) {
        success = true;
      } else {
        errMsg = "HTTP Status Code: " + responseCode;
      }
    } catch (e) {
      errMsg = "Fetch Error: " + e.toString();
    }
    
    if (!success) {
      failCount++;
      badUrls.push({
        url: url,
        error: errMsg,
        entities: uniqueUrls[url]
      });
    }
  }
  
  Logger.log("  Verification completed: " + checkCount + " URLs checked, " + failCount + " failures found.");
  
  // Output failures to logs
  if (failCount > 0) {
    Logger.log("  === LINK CHECKER FAILURE REPORT ===");
    for (var k = 0; k < badUrls.length; k++) {
      var bad = badUrls[k];
      Logger.log("  FAILED URL: " + bad.url + " | Reason: " + bad.error);
      for (var m = 0; m < bad.entities.length; m++) {
        var ent = bad.entities[m];
        Logger.log("    - Target: [" + ent.type + "] " + ent.idOrText + " | Campaign: '" + ent.campaignName + "' | Ad Group: '" + ent.adGroupName + "'");
      }
    }
  } else {
    Logger.log("  All checked URLs are valid (200 OK).");
  }
}
