# IFB-Wrapper
iFormBuilder API Wrapper

## Installation
TO BE ADDED

## Getting Started
TO BE ADDED

## How to Contribute
TO BE ADDED

## iFormBuilder Resource Reference

### Currently Unsupported Resources
- Shared Page
- Page Feed
- Page Email Alert
- Trigger Record Post
- Notification
- Private Media
- Device License

### Token Resource
| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Token | requestAccessToken() |

### Profile
| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Profile | createProfile |
| GET | Profile | readProfile |
| GET | Profiles | readProfiles |
| GET | * | readAllProfiles |
| PUT | Profile | updateProfile |
| DELETE | Profile | deleteProfile |
| DELETE | Profiles | deleteProfiles |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| GET | Company Info | readCompanyInfo |

### User
| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Users | createUsers |
| GET | User | readUser |
| GET | Users | readUsers |
| GET | * | readAllUsers |
| PUT | User | updateUser |
| PUT | Users | updateUsers |
| DELETE | User | deleteUser |
| DELETE | Users | deleteUsers |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | User Groups | createUserGroups |
| GET | User | readUserGroup |
| GET | User Groups | readUserGroups |
| PUT | User Group | updateUserGroup |
| PUT | User Groups | updateUserGroups |
| DELETE | User Group | deleteUserGroup |
| DELETE | User Groups | deleteUserGroups |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | User Page Assignments | createUserPageAssignments |
| GET | User Page Assignment | readUserPageAssignment |
| GET | User Page Assignments | readUserPageAssignments |
| GET | * | readAllUserPageAssignments |
| PUT | User Page Assignment | updateUserPageAssignment |
| PUT | User Page Assignments | updateUserPageAssignments |
| DELETE | User Page Assignment | deleteUserPageAssignment |
| DELETE | User Page Assignments | deleteUserPageAssignments |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | User Record Assignments | createUserRecordAssignments |
| GET | User Record Assignment | readUserRecordAssignment |
| GET | User Record Assignments | readUserRecordAssignments |
| PUT | User Record Assignment | updateUserRecordAssignment |
| PUT | User Record Assignments | updateUserRecordAssignments |
| DELETE | User Record Assignment | deleteUserRecordAssignment |
| DELETE | User Record Assignments | deleteUserRecordAssignments |

### Page
| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Page | createPage |
| GET | Page | readPage |
| GET | Pages | readPages |
| GET | * | readAllPages |
| PUT | Page | updatePage |
| PUT | Pages | updatePages |
| DELETE | Page | deletePage |
| DELETE | Pages | deletePages |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Page Group | createPageGroup |
| GET | Page Group | readPageGroup |
| GET | Page Groups | readPageGroups |
| PUT | Page Group | updatePageGroup |
| PUT | Page Groups | updatePageGroups |
| DELETE | Page Group | deletePageGroup |
| DELETE | Page Groups | deletePageGroups |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Page Assignments | createPageAssignments |
| GET | Page Assignment | readPageAssignment |
| GET | Page Assignments | readPageAssignments |
| GET | * | readAllPageAssignments |
| PUT | Page Assignment | updatePageAssignment |
| PUT | Page Assignments | updatePageAssignments |
| DELETE | Page Assignment | deletePageAssignment |
| DELETE | Page Assignments | deletePageAssignments |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Page Record Assignments | createPageRecordAssignments |
| GET | Page Record Assignment | readPageRecordAssignment |
| GET | Page Record Assignments | readPageRecordAssignments |
| PUT | Page Record Assignment | updatePageRecordAssignment |
| PUT | Page Record Assignments | updatePageRecordAssignments |
| DELETE | Page Record Assignment | deletePageRecordAssignment |
| DELETE | Page Record Assignments | deletePageRecordAssignments |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Page Dynamic Attributes | createPageDynamicAttributes |
| GET | Page Dynamic Attribute | readPageDynamicAttribute |
| GET | Page Dynamic Attributes | readPageDynamicAttributes |
| PUT | Page Dynamic Attribute | updatePageDynamicAttribute |
| PUT | Page Dynamic Attributes | updatePageDynamicAttributes |
| DELETE | Page Dynamic Attribute | deletePageDynamicAttribute |
| DELETE | Page Dynamic Attributes | deletePageDynamicAttributes |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Page Localizations | createPageLocalizations |
| GET | Page Localization | readPageLocalization |
| GET | Page Localizations | readPageLocalizations |
| PUT | Page Localization | updatePageLocalization |
| PUT | Page Localizations | updatePageLocalizations |
| DELETE | Page Localization | deletePageLocalization |
| DELETE | Page Localizations | deletePageLocalizations |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | HTTP Callback | createPageEndpoints |
| GET | HTTP Callback | readPageEndpoint |
| GET | HTTP Callbacks | readPageEndpoints |
| PUT | HTTP Callback | updatePageEndpoint |
| PUT | HTTP Callbacks | updatePageEndpoints |
| DELETE | HTTP Callback | deletePageEndpoint |
| DELETE | HTTP Callbacks | deletePageEndpoints |

### Element
| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Elements | createElements |
| GET | Element | readElement |
| GET | Elements | readElements |
| GET | * | readAllElements |
| PUT | Element | updateElement |
| PUT | Elements | updateElements |
| DELETE | Element | deleteElement |
| DELETE | Elements | deleteElements |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Element Dynamic Attributes | createElementDynamicAttributes |
| GET | Element Dynamic Attribute | readElementDynamicAttribute |
| GET | Element Dynamic Attributes | readElementDynamicAttributes |
| PUT | Element Dynamic Attribute | updateElementDynamicAttribute |
| PUT | Element Dynamic Attributes | updateElementDynamicAttributes |
| DELETE | Element Dynamic Attribute | deleteElementDynamicAttribute |
| DELETE | Element Dynamic Attributes | deleteElementDynamicAttributes |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Element Localizations | createElementLocalizations |
| GET | Element Localization | readElementLocalization |
| GET | Element Localizations | readElementLocalizations |
| PUT | Element Localization | updateElementLocalization |
| PUT | Element Localizations | updateElementLocalizations |
| DELETE | Element Localization | deleteElementLocalization |
| DELETE | Element Localizations | deleteElementLocalizations |

### Option List
| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Option List | createOptionList |
| GET | Option List | readOptionList |
| GET | Option Lists | readOptionLists |
| GET |  | readAllOptionLists |
| PUT | Option List | updateOptionList |
| PUT | Option Lists | updateOptionLists |
| DELETE | Option List | deleteOptionList |
| DELETE | Option Lists | deleteOptionLists |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| GET | Option List Dependencies | readOptionListDependencies |

### Option
| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Options | createOptions |
| GET | Option | readOption |
| GET | Options | readOptions |
| GET | * | readAllOptions |
| PUT | Option | updateOption |
| PUT | Options | updateOptions |
| DELETE | Option | deleteOption |
| DELETE | Options | deleteOptions |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Option Localizations | createOptionLocalizations |
| GET | Option Localization | readOptionLocalization |
| GET | Option Localizations | readOptionLocalizations |
| PUT | Option Localization | updateOptionLocalization |
| PUT | Option Localizations | updateOptionLocalizations |
| DELETE | Option Localization | deleteOptionLocalization |
| DELETE | Option Localizations | deleteOptionLocalizations |

### Record
| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Records | createRecords |
| GET | Record | readRecord |
| GET | Records | readRecords |
| GET | * | readAllRecords |
| PUT | Record | updateRecord |
| PUT | Records | updateRecords |
| DELETE | Record | deleteRecord |
| DELETE | Records | deleteRecords |

| Method | Resource | Function |
|:------:|:--------:|:--------:|
| POST | Record Assignments | createRecordAssignments |
| GET | Record Assignment | readRecordAssignment |
| GET | Record Assignments | readRecordAssignments |
| PUT | Record Assignment | updateRecordAssignment |
| PUT | Record Assignments | updateRecordAssignments |
| DELETE | Record Assignment | deleteRecordAssignment |
| DELETE | Record Assignments | deleteRecordAssignments |