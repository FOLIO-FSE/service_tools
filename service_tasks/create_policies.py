import json, uuid
from abc import abstractmethod

import requests
from folioclient import FolioClient

from service_tasks.service_task_base import ServiceTaskBase


class CreateCircPolicies(ServiceTaskBase):
    def __init__(self, folio_client: FolioClient, args):
        print(args)
        super().__init__(folio_client)

    def do_work(self):
        # request policies
        rp = []
        rp.append({
              "id" : "81ee4250-7809-4558-9852-a7bde938e3f0",
              "name" : "Noncirculating",
              "requestTypes" : [ ],
              })
        rp.append({
              "id" : "432f881b-619a-4ccb-9c1c-8c8968a1efeb",
              "name" : "Page only",
              "requestTypes" : [ "Page"],
               })
        rp.append({
             "id" : "d17480aa-57a2-465d-aa60-3b45efd36b30",
              "name" : "Hold only",
              "requestTypes" : [ "Hold"],
              })
        rp.append({
              "id" : "0dd19c5c-a89d-4e79-b7ab-2893ba0e458d",
              "name" : "Hold, Page, Recall",
               "requestTypes" : [ "Hold", "Page", "Recall" ],
               })
        # patron notices
        pn = []
        pn.append({
            "id" : "61d89ecf-887b-4699-abb7-707ab22da821",
            "outputFormats" : [ "text/html" ],
            "templateResolver" : "mustache",
            "localizedTemplates" : {
            "en" : {
            "header" : "Cancellation Notice",
            "body" : "<div>{{item.effectiveLocationLibrary}}</div><div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>We regret that your request for the following item(s) has been cancelled.</div><div><br></div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><br></div><div>In most cases cancellations occur because the item was not available by the \"not needed after\" date you specified in your original request.</div><div>&nbsp;</div><div>Please contact the library staff if you still have a need for this item.</div><div>&nbsp;</div><div>If you have any questions please contact us at the indicated location.</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Phone: </strong>(XXX)XXX-XXXX</div>",  
            "attachments" : [ ] 
            }
            },
            "name" : "Cancellation Notice",
            "active" : "true",
            "category" : "Request"
            })
        pn.append({
            "id" : "6571d5e8-e2ce-4636-b271-41553cf33a62",
            "outputFormats" : [ "text/html" ],
            "templateResolver" : "mustache",
            "localizedTemplates" : {
                "en" : {
                    "header" : "Item Available Notice",
                    "body" : "<div>{{request.servicePointPickup}}</div><div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>The item(s) that you requested are now available at the location(s) shown below. Please pick up item(s) before the indicated expiration date.</div><div><br></div><div><strong>Location</strong>: {{request.servicePointPickup}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Expiration Date</strong>: {{request.holdShelfExpirationDate}}</div><div><br></div><div>If you have any questions please contact us at the indicated location.</div><div><strong>Location</strong>: {{request.servicePointPickup}}</div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div>",
                    "attachments" : [ ]
                    }
                },
            "name" : "Item Available Notice",
            "active" : "true",
            "category" : "Request"
            })
        pn.append({
            "id" : "1c58a85d-c779-4ce4-9d21-b56ae84f3865",
            "outputFormats" : [ "text/html" ],
            "templateResolver" : "mustache",
            "localizedTemplates" : {
                "en" : {
                    "header" : "Recall- Overdue Notice",
                    "body" : "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}},</div><div><br></div><div>Please return the following recalled item(s) immediateley to the indicated location. Fines will be assessed for overdue recalled library material(s). A fine of $1.00 per day with a maximum fine amount of $20.00 will be charged to your account for each item not returned by the recalled due date(s).</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Notification Number</strong>: XXX</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>{{/loans}}</div><div>Fines for overdue recalled items are substantial and increase the longer you keep the item. Please return the urgently needed item(s).</div><div>&nbsp;</div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone</strong>: (XXX)XXX-XXXX</div>",
                    "attachments" : [ ]
                    }
                },
            "name" : "Recall Overdue Notice",
            "active" : "true",
            "category" : "Loan"
            })
        pn.append({
            "id" : "71f1f163-050e-42f0-9b1f-be13342bbe46",
            "outputFormats" : [ "text/html" ],
            "templateResolver" : "mustache",
            "localizedTemplates" : {
                "en" : {
                    "header" : "Courtesy Notice",
                    "body" : "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>This notice is to remind you that these item(s) will be due soon. To renew your item(s) please log in to to your library account <a href=\"http://library.ua.edu/vwebv/myAccount\" rel=\"noopener noreferrer\" target=\"_blank\" style=\"color: windowtext;\">http://library.ua.edu/vwebv/myAccount </a>. Please verify that your items were renewed. Some items are not renewable. If your items were not renewed and/or you have any questions, please contact us at the indicated location(s).</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Notification Number:</strong> XXX</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Copy #</strong>: {{item.copy}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>{{/loans}}</div><div>Please return the item(s) or have the item(s) renewed.</div><div><br></div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone:</strong> (XXX)XXX-XXXX</div><div><br></div>",
                "attachments" : [ ]
                }
                },
                "name" : "Courtesy Notice",
                "active" : "true",
                "category" : "Loan"
                })
        pn.append({
            "id" : "bffeef62-1913-4643-b776-ed4e67d4a483",
            "outputFormats" : [ "text/html" ],
            "templateResolver" : "mustache",
            "localizedTemplates" : { 
                "en" : { 
                    "header" : "Recall Notice", 
                    "body" : "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>The following item(s) currently charged to you are needed by another patron. The new due date(s) are shown below. Please return item(s) to the indicated location(s). Fines will be assessed for items not returned by the new due date(s). A fine of $1.00 per day with a maximum fine amount of $20.00 will be charged to your account if item(s) are returned after the new due date(s).</div><div><br></div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>If you have any questions please contact us at the indicated location:</div><div><br></div><div><strong>Phone: </strong>(XXX)XXX-XXXX</div>",
                "attachments" : [ ]
                }
                },
            "name" : "Recall Notice",
            "active" : "true",
            "category" : "Loan"
            })
        pn.append({
            "id": "c3213107-c92b-40d2-9710-6293cbc111b9",
            "outputFormats": [ "text/html" ],
            "templateResolver": "mustache",
            "localizedTemplates": { 
                "en" : { 
                    "header" : "Overdue Notice", 
                    "body" : "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>Please renew the following items or return to the locations indicated as soon as possible. Items can be renewed by logging into your library account at http://library.ua.edu/vwebv/myAccount. Please verify that your items were renewed. Some items may not be renewable.</div><div><br></div><div>Fines will be assessed for overdue library materials. Books that are are considered lost will be charged to your account for each item. </div><div><br></div><div>More information about fines and fees can be found at lib.ua.edu/using-the-library/circulation-services/fines/. If you have any questions, please contact us at the indicated location(s).</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Notification Number</strong>:&nbsp;XXX</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><br></div><div>{{/loans}}</div><div>If you are liable for overdue fines remember that the fine increases the longer you keep the item. You may also be charged if item is not returned.</div><div><br></div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone</strong>: (XXX)XXX-XXXX</div>",
                "attachments": [ ]
                }
                },
            "name": "Overdue Notice",
            "active": "true",
            "category": "Loan"
            })
        pn.append({
            "id" : "defcdf02-0d87-490d-8f04-29ff41361202",
            "outputFormats" : [ "text/html" ],
            "templateResolver" : "mustache",
            "localizedTemplates" : { 
                "en" : {
                    "header" : "Notice of Fine or Fee",
                    "body" : "<div><br></div><div>Dear {{user.firstName}} {{user.lastName}}:</div><div><br></div><div>The following is a list of current fine(s) or fee(s). More detailed information is available at the library. For payment information, please contact us at the indicated location(s). Information about fines and fees can be found at lib.ua.edu/using-the-library/circulation-services/fines/.</div><div><br></div><div>{{#loans}}</div><div><strong>Location</strong>: {{item.effectiveLocationLibrary}}</div><div><strong>Title</strong>: {{item.title}}</div><div><strong>Author</strong>: {{item.primaryContributor}}</div><div><strong>Item ID</strong>: {{item.barcode}}</div><div><strong>Call #</strong>: {{item.callNumber}}</div><div><strong>Due Date</strong>: {{loan.dueDate}}</div><div><strong>Due Date when Fined</strong>: XXX</div><div><strong>Fine/Fee Date</strong>: {{feeCharge.chargeDateTime}}</div><div><strong>Description</strong>: {{feeCharge.type}}</div><div><strong>Fine/Fee Amount</strong>: {{feeCharge.amount}}</div><div><strong>Fine/Fee Balance</strong>: {{feeCharge.remainingAmount}</div><div><strong>Previously Billed: </strong>XXX</div><div><br></div><div>{{/loans}}</div><div><br></div><div><strong>Total of all Fines and Fees</strong>: XXX</div><div><br></div><div>If you have any questions please contact us at the indicated location.</div><div><br></div><div><strong>Phone</strong>:<strong> </strong>(XXX)XXX-XXXX</div>",
                "attachments" : [ ]
                }
                },
            "name" : "Notice of Fine or Fee",
            "active" : "true",
            "category" : "AutomatedFeeFine"
            })
        # patron notice policies
        pnp = []
        pnp.append({
            "id" : "41a1cd99-97be-4c2e-938d-733f45bd0c43",
            "name" : "Standard Notice Policy",
            "active" : "true",
            "loanNotices" : [ {
                "templateId" : "bffeef62-1913-4643-b776-ed4e67d4a483",
                "format" : "Email",
                "realTime" : "false",
                "sendOptions" : {
                    "sendWhen" : "Item recalled"
                    }
                }, {
                    "templateId" : "71f1f163-050e-42f0-9b1f-be13342bbe46",
                    "format" : "Email",
                    "frequency" : "Recurring",
                    "realTime" : "false",
                    "sendOptions" : {
                        "sendHow" : "Before",
                        "sendWhen" : "Due date",
                        "sendBy" : {
                            "duration" : 1,
                            "intervalId" : "Days"
                            },
                        "sendEvery" : {
                            "duration" : 1,
                            "intervalId" : "Days"
                            }
                        }
                    }, {
                        "templateId" : "c3213107-c92b-40d2-9710-6293cbc111b9",
                        "format" : "Email",
                        "frequency" : "Recurring",
                        "realTime" : "false",
                        "sendOptions" : {
                            "sendHow" : "After",
                            "sendWhen" : "Due date",
                            "sendBy" : {
                                "duration" : 1,
                                "intervalId" : "Days"
                                },
                            "sendEvery" : {
                                "duration" : 1,
                                "intervalId" : "Days"
                                }
                            }
                        } ],
                    "feeFineNotices" : [ {
                        "templateId" : "defcdf02-0d87-490d-8f04-29ff41361202",
                        "format" : "Email",
                        "realTime" : "true",
                        "sendOptions" : {
                            "sendHow" : "Upon At",
                            "sendWhen" : "Overdue fine returned"
                            }
                        } ],
                    "requestNotices" : [ {
                        "templateId" : "61d89ecf-887b-4699-abb7-707ab22da821",
                        "format" : "Email",
                        "realTime" : "false",
                        "sendOptions" : {
                            "sendWhen" : "Request cancellation"
                            }
                        }, {
                            "templateId" : "6571d5e8-e2ce-4636-b271-41553cf33a62",
                            "format" : "Email",
                            "realTime" : "false",
                            "sendOptions" : {
                                "sendWhen" : "Available"
                                }
                            } ]
                        })
        # lost item fee policies
        lif = []
        lif.append({
            "name" : "No Lost Fees",
            "itemAgedLostOverdue" : {
                "duration" : 30,
                "intervalId" : "Days"
                },
            "chargeAmountItem" : {
                "chargeType" : "actualCost",
                "amount" : 0.0
                },
            "lostItemProcessingFee" : 0.0,
            "chargeAmountItemPatron" : "false",
            "chargeAmountItemSystem" : "false",
            "lostItemChargeFeeFine" : {
                "duration" : 99,
                "intervalId" : "Months"
                },
            "returnedLostItemProcessingFee" : "false",
            "replacedLostItemProcessingFee" : "false",
            "replacementProcessingFee" : 0.0,
            "replacementAllowed" : "true",
            "lostItemReturned" : "Remove",
            "id" : "dc39c32c-b2fb-4097-b50d-04ab2d6c3f87"
            })
        lif.append({
            "name" : "Standard cost with fee",
            "itemAgedLostOverdue" : {
                "duration" : 30,
                "intervalId" : "Days"
                },
            "patronBilledAfterAgedLost" : {
                "duration" : 15,
                "intervalId" : "Days"
                },
            "chargeAmountItem" : {
                "chargeType" : "anotherCost",
                "amount" : 50.0
                },
            "lostItemProcessingFee" : 10.0,
            "chargeAmountItemPatron" : "true",
            "chargeAmountItemSystem" : "true",
            "lostItemChargeFeeFine" : {
                "duration" : 99,
                "intervalId" : "Months"
                },
            "returnedLostItemProcessingFee" : "true",
            "replacedLostItemProcessingFee" : "true",
            "replacementProcessingFee" : 25.0,
            "replacementAllowed" : "true",
            "lostItemReturned" : "Charge",
            "id" : "ca0cbf21-172a-45ff-a081-fd289b40e4a4"
            })
        lif.append({
            "name" : "Bill actual cost",
            "itemAgedLostOverdue" : {
                "duration" : 30,
                "intervalId" : "Days"
                },
            "patronBilledAfterAgedLost" : {
                "duration" : 1,
                "intervalId" : "Days"
                },
            "chargeAmountItem" : {
                "chargeType" : "actualCost",
                "amount" : 0.0
                },
            "lostItemProcessingFee" : 0.0,
            "chargeAmountItemPatron" : "false",
            "chargeAmountItemSystem" : "false",
            "lostItemChargeFeeFine" : {
                "duration" : 1,
                "intervalId" : "Months"
                },
            "returnedLostItemProcessingFee" : "true",
            "replacedLostItemProcessingFee" : "true",
            "replacementProcessingFee" : 0.0,
            "replacementAllowed" : "true",
            "lostItemReturned" : "Charge",
            "feesFinesShallRefunded" : {
                "duration" : 12,
                "intervalId" : "Months"
                },
            "id" : "6d66ef56-258c-4443-a962-950aff191c22"
            })
        lif.append({
            "name" : "Lost Reserve Equipment Policy",
            "itemAgedLostOverdue" : {
                "duration" : 7,
                "intervalId" : "Days"
                },
            "patronBilledAfterAgedLost" : {
                "duration" : 2,
                "intervalId" : "Days"
                },
            "chargeAmountItem" : {
                "chargeType" : "actualCost",
                "amount" : 0.0
                },
            "lostItemProcessingFee" : 0.0,
            "chargeAmountItemPatron" : "true",
            "chargeAmountItemSystem" : "true",
            "lostItemChargeFeeFine" : {
                "duration" : 1,
                "intervalId" : "Months"
                },
            "returnedLostItemProcessingFee" : "true",
            "replacedLostItemProcessingFee" : "true",
            "replacementProcessingFee" : 0.0,
            "replacementAllowed" : "true",
            "lostItemReturned" : "Charge",
            "feesFinesShallRefunded" : {
                "duration" : 2,
                "intervalId" : "Weeks"
                },
            "id" : "a389c71a-62ea-40f7-8e2d-07eb176fb5a4"
            })
        lif.append({
            "name" : "Lost Hourly Reserve Item Policy",
            "itemAgedLostOverdue" : {
                "duration" : 1,
                "intervalId" : "Days"
                },
            "patronBilledAfterAgedLost" : {
                "duration" : 1,
                "intervalId" : "Days"
                },
            "chargeAmountItem" : {
                "chargeType" : "actualCost",
                "amount" : 0.0
                },
            "lostItemProcessingFee" : 0.0,
            "chargeAmountItemPatron" : "true",
            "chargeAmountItemSystem" : "true",
            "lostItemChargeFeeFine" : {
                "duration" : 1,
                "intervalId" : "Months"
                },
            "returnedLostItemProcessingFee" : "true",
            "replacedLostItemProcessingFee" : "true",
            "replacementProcessingFee" : 0.0,
            "replacementAllowed" : "true",
            "lostItemReturned" : "Charge",
            "feesFinesShallRefunded" : {
                "duration" : 3,
                "intervalId" : "Days"
                },
            "id" : "7ad3078c-5a39-455b-80a6-97b779758b4f"
            })
        # overdue fee policies
        od = []
        od.append({
            "name" : "No Overdue",
            "countClosed" : "true",
            "maxOverdueFine" : 0.0,
            "forgiveOverdueFine" : "false",
            "gracePeriodRecall" : "false",
            "maxOverdueRecallFine" : 0.0,
            "id" : "b6525ee0-7a2b-4aee-9145-77ddc08ed407"
            })
        od.append({
            "name" : "Recall Fines Only",
            "description" : "Fines for recalled items",
            "countClosed" : "false",
            "maxOverdueFine" : 0.0,
            "forgiveOverdueFine" : "true",
            "overdueRecallFine" : {
                "quantity" : 1.0,
                "intervalId" : "day"
                },
            "gracePeriodRecall" : "true",
            "maxOverdueRecallFine" : 25.0,
            "id" : "9aefffc4-1ac6-4a5f-bf31-d16c22ced7a5"
            })
        od.append({
            "name" : "Hourly Reserves Fines and Recall Fines",
            "overdueFine" : {
                "quantity" : 0.25,
                "intervalId" : "hour"
                },
            "countClosed" : "false",
            "maxOverdueFine" : 25.0,
            "forgiveOverdueFine" : "true",
            "overdueRecallFine" : {
                "quantity" : 1.0,
                "intervalId" : "day"
                },
            "gracePeriodRecall" : "true",
            "maxOverdueRecallFine" : 25.0,
            "id" : "5202c6b9-ab43-40f1-930b-bf5e19f05307"
            })
        # loan policies
        lp = []
        lp.append({
            "id" : "0bec934a-931a-4538-88fb-da035555f5c5",
            "name" : "Non circulating",
            "loanable" : "false",
            "renewable" : "false"
            })
        lp.append({
            "id" : "43198de5-f56a-4a53-a0bd-5a324418967a",
            "name" : "2 Hours",
            "loanable" : "true",
            "loansPolicy" : {
                "profileId" : "Rolling",
                "period" : {
                    "duration" : 2,
                    "intervalId" : "Hours"
                    },
                "closedLibraryDueDateManagementId" : "CURRENT_DUE_DATE_TIME"
                },
            "renewable" : "true",
            "renewalsPolicy" : {
                "unlimited" : "false",
                "numberAllowed" : 3.0,
                "renewFromId" : "SYSTEM_DATE",
                "differentPeriod" : "false"
                }
            })
        lp.append({
            "id" : "cec37e21-9bed-441d-8fe5-ed39cf2469c3",
            "name" : "1 Day - no renewals",
            "loanable" : "true",
            "loansPolicy" : {
                "profileId" : "Rolling",
                "period" : {
                    "duration" : 1,
                    "intervalId" : "Days"
                    },
                "closedLibraryDueDateManagementId" : "END_OF_THE_NEXT_OPEN_DAY",
                "gracePeriod" : {
                    "duration" : 1,
                    "intervalId" : "Days"
                    },
                "itemLimit" : 10
                },
            "renewable" : "false",
            "requestManagement" : {
                "recalls" : {
                    "minimumGuaranteedLoanPeriod" : {
                        "duration" : 1,
                        "intervalId" : "Days"
                        }
                    }
                }
            })
        lp.append({
            "id" : "5fb5b2ce-a2a3-4ab2-8e88-ea17e77f9352",
            "name" : "7 Day",
            "loanable" : "true",
            "loansPolicy" : {
                "profileId" : "Rolling",
                "period" : {
                    "duration" : 7,
                    "intervalId" : "Days"
                    },
                "closedLibraryDueDateManagementId" : "END_OF_THE_NEXT_OPEN_DAY",
                "gracePeriod" : {
                    "duration" : 1,
                    "intervalId" : "Days"
                    }
                },
            "renewable" : "true",
            "renewalsPolicy" : {
                "numberAllowed" : 1.0,
                "renewFromId" : "CURRENT_DUE_DATE"
                },
            "requestManagement" : {
                "recalls" : {
                    "minimumGuaranteedLoanPeriod" : {
                        "duration" : 7,
                        "intervalId" : "Days"
                        }
                    }
                }
            })
        lp.append({
            "id" : "c937bb25-91e9-4ddf-a416-139d5a4e73ae",
            "name" : "4 week - no renewals",
            "loanable" : "true",
            "loansPolicy" : {
                "profileId" : "Rolling",
                "period" : {
                    "duration" : 28,
                    "intervalId" : "Days"
                    },
                "closedLibraryDueDateManagementId" : "END_OF_THE_NEXT_OPEN_DAY",
                "gracePeriod" : {
                    "duration" : 1,
                    "intervalId" : "Days"
                    }
                },
            "renewable" : "false",
            "requestManagement" : {
                "recalls" : {
                    "minimumGuaranteedLoanPeriod" : {
                        "duration" : 14,
                        "intervalId" : "Days"
                        }
                    }
                }
            })
        lp.append({
            "id" : "4f20978b-d278-4df5-8ecf-ad4d0f0ac130",
            "name" : "4 week - 2 renewals",
            "loanable" : "true",
            "loansPolicy" : {
                "profileId" : "Rolling",
                "period" : {
                    "duration" : 28,
                    "intervalId" : "Days"
                    },
                "closedLibraryDueDateManagementId" : "END_OF_THE_NEXT_OPEN_DAY",
                "gracePeriod" : {
                    "duration" : 1,
                    "intervalId" : "Days"
                    },
                "itemLimit" : 25
                },
            "renewable" : "true",
            "renewalsPolicy" : {
                "numberAllowed" : 2.0,
                "renewFromId" : "CURRENT_DUE_DATE"
                },
            "requestManagement" : {
                "recalls" : {
                    "minimumGuaranteedLoanPeriod" : {
                        "duration" : 14,
                        "intervalId" : "Days"
                        },
                    "recallReturnInterval" : {
                        "duration" : 7,
                        "intervalId" : "Days"
                        }
                    }
                }
            })
        lp.append({
            "id" : "6ae1efaf-1876-4724-be4a-fec624ca4434",
            "name" : "6 Month",
            "loanable" : "true",
            "loansPolicy" : {
                "profileId" : "Rolling",
                "period" : {
                    "duration" : 6,
                    "intervalId" : "Months"
                    },
                "closedLibraryDueDateManagementId" : "END_OF_THE_NEXT_OPEN_DAY",
                "gracePeriod" : {
                    "duration" : 1,
                    "intervalId" : "Days"
                    }
                },
            "renewable" : "true",
            "renewalsPolicy" : {
                "unlimited" : "false",
                "numberAllowed" : 2.0,
                "renewFromId" : "SYSTEM_DATE"
                },
            "requestManagement" : {
                "recalls" : {
                    "minimumGuaranteedLoanPeriod" : {
                        "duration" : 14,
                        "intervalId" : "Days"
                        },
                    "recallReturnInterval" : {
                        "duration" : 7,
                        "intervalId" : "Days"
                        }
                    },
                "holds" : {
                    "alternateCheckoutLoanPeriod" : {
                        "duration" : 3,
                        "intervalId" : "Weeks"
                        }
                    }
                }
            })

        self.add_policy("Request", rp, "request-policy-storage/request-policies")
        self.add_policy("Patron Notice Templates", pn, "templates")
        self.add_policy("Patron Notice", pnp, "patron-notice-policy-storage/patron-notice-policies")
        self.add_policy("Lost Item", lif, "lost-item-fees-policies")
        self.add_policy("Overdue Fine", od, "overdue-fines-policies")
        self.add_policy("Loan", lp, "loan-policy-storage/loan-policies")

    def add_policy(self, description, policy_array, url):
        print(f"\n------------------- Creating {description} policies --------------\n")

        for policy in policy_array:
            print(policy)
            resp = requests.post(f"{self.folio_client.okapi_url}/{url}", data=json.dumps(policy), headers=self.folio_client.okapi_headers)
            print(f"{resp.content}")

    @staticmethod
    @abstractmethod
    def add_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)

    @staticmethod
    @abstractmethod
    def add_cli_arguments(parser):
        ServiceTaskBase.add_common_arguments(parser)
