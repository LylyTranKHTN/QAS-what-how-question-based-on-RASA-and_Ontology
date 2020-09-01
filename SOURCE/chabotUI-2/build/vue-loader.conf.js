var model =
{
  fields =[
    {
      title="text",
      id="name",
      validate={
        condition="name === ''",
        message="text can not be null.",
      },
      hide=false,
    },
    {
      title="number",
      id="phone",
      validate={
        condition="phone.length != 10",
        message="Phone number should be 10 digits."
      },
    },
    {
      title="Select",
      id="status",
      validate={
        condition="",
        message="",
      },
      type="single",
      options=[
      {
        value: 1,
        label: 'option 1',
      },
      {
        value: 2,
        label: 'option 2',
      },
    ]
    },
    {
      title="Select",
      id="status",
      validate={
        condition="",
        message="",
      },
      options=[
      {
        value: 1,
        label: 'option 1',
      },
      {
        value: 2,
        label: 'option 2',
      },
    ]
    }
  ]
}
