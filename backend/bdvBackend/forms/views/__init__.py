from .formViews import ViewFormsIndex, ViewFormDetail, CreateUpdateForm, DeleteForm
from .responseViews import ViewResponseIndex, ViewResponseDetail, NewResponse, UpdateResponse, DeleteResponse
from .questionViews import ViewQuestions, CreateQuestion, UpdateQuestion, DeleteQuestion
from .respondentViews import ViewRespondentsIndex, ViewRespondentDetail, CreateRespondent, UpdateRespondent, DeleteRespondent
from .mobileAPIViews import GetForms, SyncMobileResponses
from .siteAPIViews import GetFormInfo, GetQuestions, GetQuestionInfo, GetQuestionResponses
from .dashboardViews import Dashboard, GetData, GetQuestionData
from .fileUploadViews import FormTemplate